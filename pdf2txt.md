
2. 使用 Homebrew 安装 ocrmypdf


brew install ocrmypdf


 brew install tesseract


 brew install tesseract-lang


 ocrmypdf --version


 ocrmypdf 输入文件.pdf 输出文件.pdf



对中文 PDF 进行 OCR
ocrmypdf --force-ocr -l chi_sim+eng --sidecar output.txt --output-type none input.pdf - > /dev/null


 ocrmypdf -l chi_sim --force-ocr --rotate-pages --deskew 输入.pdf 输出.pdf