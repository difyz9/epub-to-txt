import zipfile
import os
import re
from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """从 HTML 中提取纯文本"""

    SKIP_TAGS = {'script', 'style', 'head'}
    BLOCK_TAGS = {'p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'td', 'th', 'blockquote', 'pre'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.result = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in self.SKIP_TAGS:
            self._skip += 1
        # 块级开始标签前也保证换行（避免文字紧连）
        elif t in self.BLOCK_TAGS and self._skip == 0:
            self.result.append('\n')

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in self.SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif t in self.BLOCK_TAGS and self._skip == 0:
            self.result.append('\n')

    def handle_data(self, data):
        if self._skip == 0:
            # 将非断空格替换为普通空格
            data = data.replace('\xa0', ' ')
            self.result.append(data)

    def get_text(self):
        raw = ''.join(self.result)
        # 逐行清洗：去首尾空白，去纯空白行
        lines = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                lines.append(line)
            else:
                # 保留段落间一个空行
                if lines and lines[-1] != '':
                    lines.append('')
        # 去掉末尾多余空行
        while lines and lines[-1] == '':
            lines.pop()
        return '\n'.join(lines)


def extract_epub_text(epub_path: str, output_path: str):
    """解析 EPUB 文件，将所有文本内容写入 TXT 文件"""

    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"找不到文件：{epub_path}")

    with zipfile.ZipFile(epub_path, 'r') as zf:
        namelist = zf.namelist()

        # 找到 OPF 文件（记录阅读顺序）
        opf_path = None
        container_path = 'META-INF/container.xml'
        if container_path in namelist:
            container_xml = zf.read(container_path).decode('utf-8', errors='replace')
            m = re.search(r'full-path="([^"]+\.opf)"', container_xml)
            if m:
                opf_path = m.group(1)

        # 按照 OPF spine 顺序读取章节
        spine_items = []
        if opf_path and opf_path in namelist:
            opf_xml = zf.read(opf_path).decode('utf-8', errors='replace')
            opf_dir = os.path.dirname(opf_path)

            # 解析 manifest：id -> href
            manifest = {}
            for m in re.finditer(r'<item[^>]+id="([^"]+)"[^>]+href="([^"]+)"', opf_xml):
                manifest[m.group(1)] = m.group(2)

            # 解析 spine：按顺序列出 idref
            spine_idrefs = re.findall(r'<itemref[^>]+idref="([^"]+)"', opf_xml)
            for idref in spine_idrefs:
                href = manifest.get(idref)
                if href:
                    # 拼接相对路径
                    if opf_dir:
                        full_path = opf_dir + '/' + href
                    else:
                        full_path = href
                    # 去掉 fragment
                    full_path = full_path.split('#')[0]
                    if full_path in namelist:
                        spine_items.append(full_path)

        # 如果没有找到 spine，退而求其次：取所有 html/xhtml 文件
        if not spine_items:
            spine_items = sorted([
                n for n in namelist
                if n.lower().endswith(('.html', '.xhtml', '.htm'))
            ])

        if not spine_items:
            raise ValueError("EPUB 中未找到任何 HTML/XHTML 内容文件")

        all_text_parts = []
        for item_path in spine_items:
            raw = zf.read(item_path).decode('utf-8', errors='replace')
            parser = HTMLTextExtractor()
            parser.feed(raw)
            text = parser.get_text()
            if text:
                all_text_parts.append(text)

    full_text = '\n\n'.join(all_text_parts)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"完成！共提取 {len(full_text)} 个字符，已保存到：{output_path}")


if __name__ == '__main__':
    epub_file = '004.epub'
    txt_file = '004.txt'
    extract_epub_text(epub_file, txt_file)
