---
name: epub-to-txt
description: Convert EPUB ebook files to plain text (TXT) format. Use this skill whenever the user wants to extract text from an EPUB file, convert an ebook to plain text, strip formatting from an EPUB, or read/process EPUB content as text. Trigger on any mention of EPUB conversion, ebook text extraction, ".epub to .txt", or requests to "read an epub file" programmatically.
---

# EPUB to TXT Converter

Convert EPUB ebook files into clean, readable plain text using the bundled script `scripts/epub_to_txt.py`.

The script uses only the Python standard library — no extra dependencies required.

## Running the conversion

Locate the script relative to this SKILL.md file at `scripts/epub_to_txt.py`.

**Single file:**
```bash
python3 <skill-dir>/scripts/epub_to_txt.py <input.epub> [output.txt]
```
- If `output.txt` is omitted, the result is saved as `<input>.txt` in the same directory as the EPUB.

**Batch conversion (all EPUBs in a folder):**
```bash
for f in /path/to/folder/*.epub; do
    python3 <skill-dir>/scripts/epub_to_txt.py "$f"
done
```

## Workflow

1. **Resolve the script path** — find `scripts/epub_to_txt.py` relative to this skill's directory.
2. **Determine paths** — confirm input EPUB exists; use user-provided output path or default (`<name>.txt`).
3. **Run the script** — execute via `python3 scripts/epub_to_txt.py <epub> [output]`.
4. **Report result** — show the output file path and size printed by the script.

## Edge cases

- **DRM-protected EPUBs**: The script raises `RuntimeError` with a clear message. Inform the user that DRM-protected files cannot be converted.
- **Image-only EPUBs** (comics/manga): No text will be extracted; the script will raise an error explaining this.
- **Non-standard EPUB structure**: The script gracefully falls back to scanning all `.html`/`.xhtml` files in the archive.

## Output format

Plain UTF-8 text with chapters separated by two blank lines. No HTML tags, no CSS.

## Example usage

```
User: 帮我把 /books/novel.epub 转成 txt
→ python3 scripts/epub_to_txt.py /books/novel.epub
→ Output: /books/novel.txt

User: convert my.epub to output.txt
→ python3 scripts/epub_to_txt.py my.epub output.txt

User: batch convert all epubs in ~/books/
→ for f in ~/books/*.epub; do python3 scripts/epub_to_txt.py "$f"; done
```
