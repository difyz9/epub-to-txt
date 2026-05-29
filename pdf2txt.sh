#!/bin/bash

# 遍历当前文件夹所有 PDF 文件
for pdf_file in *.pdf; do
    # 如果不存在就跳过
    [ -e "$pdf_file" ] || continue

    # 生成同名 txt 文件名
    txt_file="${pdf_file%.pdf}.txt"

    echo "正在处理：$pdf_file → $txt_file"

    # 执行 OCR 并导出 txt（不生成 PDF）
    ocrmypdf \
        --force-ocr \
        -l chi_sim+eng \
        --sidecar "$txt_file" \
        --output-type none \
        "$pdf_file" - > /dev/null 2>&1

    echo "✅ 完成：$txt_file"
done

echo -e "\n🎉 所有 PDF 已转换为同名 TXT！"
