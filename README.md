# Skill Demo

本项目演示如何使用 GitHub Copilot Skills（技能）扩展 AI 助手的能力。当前包含以下 skill：

- **epub-to-txt** — 将 EPUB 电子书转换为纯文本格式

---

## epub-to-txt

将 `.epub` 文件转换为 `.txt` 纯文本，使用 Python 标准库实现，无需安装额外依赖。

### 文件结构

```
.github/skills/epub-to-txt/
├── SKILL.md                   # Skill 描述与使用说明（Copilot 自动加载）
└── scripts/
    └── epub_to_txt.py         # 可复用的转换脚本
```

### 前提条件

- Python 3.6+（使用标准库，无需 pip 安装任何包）

### 方式一：通过 GitHub Copilot 自动调用

在 VS Code 中打开此项目，直接用自然语言告诉 Copilot：

> 帮我把 xxx.epub 转为 txt

Copilot 会自动识别 epub-to-txt skill 并调用脚本完成转换。

### 方式二：直接运行脚本

**转换单个文件（输出到同目录）：**

```bash
python3 .github/skills/epub-to-txt/scripts/epub_to_txt.py input.epub
# 输出：input.txt（与 epub 同目录）
```

**指定输出路径：**

```bash
python3 .github/skills/epub-to-txt/scripts/epub_to_txt.py input.epub output.txt
```

**批量转换目录下所有 EPUB：**

```bash
for f in /path/to/books/*.epub; do
    python3 .github/skills/epub-to-txt/scripts/epub_to_txt.py "$f"
done
```

### 示例

```bash
$ python3 .github/skills/epub-to-txt/scripts/epub_to_txt.py 002.epub
✓ 转换成功: 002.txt  (431,374 字节 / 421.3 KB)
```

### 注意事项

| 情况 | 说明 |
|------|------|
| DRM 保护的 EPUB | 无法转换，脚本会给出错误提示 |
| 纯图片 EPUB（漫画等） | 无文本内容可提取，脚本会提示 |
| 非标准 EPUB 结构 | 自动降级为扫描所有 HTML 文件 |
| 编码异常字符 | 自动替换，不会中断转换 |
