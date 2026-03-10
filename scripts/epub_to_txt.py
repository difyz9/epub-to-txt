#!/usr/bin/env python3
"""
epub_to_txt.py — Convert EPUB files to plain text.

Usage:
    python3 epub_to_txt.py <input.epub> [output.txt]

If output path is omitted, saves as <input>.txt in the same directory.
"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    BLOCK_TAGS = {'p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'section', 'article'}
    SKIP_TAGS = {'script', 'style'}

    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self._skip_depth -= 1
        if tag in self.BLOCK_TAGS:
            self.parts.append('\n')

    def handle_data(self, data):
        if self._skip_depth == 0:
            self.parts.append(data)

    def get_text(self):
        return ''.join(self.parts)


def _extract_text_from_html(html_bytes):
    parser = _TextExtractor()
    parser.feed(html_bytes.decode('utf-8', errors='replace'))
    return parser.get_text().strip()


def epub_to_txt(epub_path, output_path=None):
    """
    Convert an EPUB file to plain text.

    Args:
        epub_path:   Path to the input .epub file.
        output_path: Path for the output .txt file.
                     Defaults to same directory as epub, with .txt extension.

    Returns:
        The output file path.

    Raises:
        FileNotFoundError: If epub_path does not exist.
        RuntimeError: If the EPUB structure cannot be parsed.
    """
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"File not found: {epub_path}")

    with zipfile.ZipFile(epub_path, 'r') as z:
        # Locate the OPF manifest file
        try:
            container_xml = z.read('META-INF/container.xml').decode('utf-8')
            root = ET.fromstring(container_xml)
            ns = {'cn': 'urn:oasis:names:tc:opendocument:xmlns:container'}
            opf_path = root.find('.//cn:rootfile', ns).get('full-path')
        except Exception:
            opf_path = next((n for n in z.namelist() if n.endswith('.opf')), None)
            if not opf_path:
                raise RuntimeError("Cannot find OPF manifest in EPUB — file may be malformed or DRM-protected.")

        opf_dir = os.path.dirname(opf_path)
        opf_root = ET.fromstring(z.read(opf_path).decode('utf-8'))

        ns_opf = {'opf': 'http://www.idpf.org/2007/opf'}

        # Build id → href map from manifest
        manifest = {
            item.get('id'): item.get('href')
            for item in opf_root.findall('.//opf:item', ns_opf)
        }

        # Reading order from spine; fall back to all HTML items
        spine = [ref.get('idref') for ref in opf_root.findall('.//opf:itemref', ns_opf)]
        if not spine:
            spine = [k for k, v in manifest.items()
                     if v and v.lower().endswith(('.html', '.xhtml', '.htm'))]

        chapters = []
        for idref in spine:
            href = manifest.get(idref)
            if not href:
                continue
            full_href = os.path.join(opf_dir, href).replace('\\', '/') if opf_dir else href
            try:
                raw = z.read(full_href)
            except KeyError:
                continue
            text = _extract_text_from_html(raw)
            if text:
                chapters.append(text)

    if not chapters:
        raise RuntimeError("No text content extracted — the EPUB may be image-only or DRM-protected.")

    if output_path is None:
        base = os.path.splitext(epub_path)[0]
        output_path = base + '.txt'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(chapters))

    return output_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    epub_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = epub_to_txt(epub_path, output_path)
        size = os.path.getsize(result)
        print(f"✓ 转换成功: {result}  ({size:,} 字节 / {size/1024:.1f} KB)")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
