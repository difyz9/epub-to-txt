#!/bin/bash

# 遍历当前文件夹所有 .epub 文件
for epub_file in *.epub; do
    # 文件不存在则跳过
    [ -e "$epub_file" ] || continue

    # 生成同名 txt（替换后缀）
    txt_file="${epub_file%.epub}.txt"

    echo "====================================="
    echo "正在转换：$epub_file → $txt_file"

    # 调用你的 Python 脚本转换
    python scripts/epub_to_txt.py "$epub_file"

    echo "✅ 转换完成：$txt_file"
done

echo -e "\n🎉 所有 EPUB 已全部转为同名 TXT！"
