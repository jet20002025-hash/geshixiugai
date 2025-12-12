# 测试 LibreOffice 转换 - 正确命令

## ✅ 正确的测试命令

根据你找到的文档，使用以下命令：

```bash
# 使用实际的文档ID
libreoffice --headless --convert-to pdf --outdir /tmp /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 检查是否生成 PDF
ls -lh /tmp/preview.pdf
```

## 🔍 或者进入文档目录测试

```bash
# 1. 进入文档目录
cd /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc

# 2. 检查文件是否存在
ls -lh preview.docx

# 3. 在当前目录执行转换
libreoffice --headless --convert-to pdf --outdir . preview.docx

# 4. 检查是否生成 PDF
ls -lh preview.pdf
```

## 📋 完整测试步骤

```bash
# 1. 进入文档目录
cd /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc

# 2. 检查文件
echo "=== 检查文件 ==="
ls -lh preview.docx

# 3. 执行转换
echo "=== 开始转换 ==="
libreoffice --headless --convert-to pdf --outdir . preview.docx

# 4. 检查结果
echo "=== 检查结果 ==="
if [ -f "preview.pdf" ]; then
    echo "✅ PDF 生成成功！"
    ls -lh preview.pdf
    file preview.pdf
else
    echo "❌ PDF 生成失败"
    echo "检查 LibreOffice 错误信息..."
fi
```

## 🐛 如果仍然失败

如果转换失败，检查：

1. **文件权限**：
```bash
ls -l preview.docx
```

2. **LibreOffice 版本**：
```bash
libreoffice --version
```

3. **详细错误信息**：
```bash
libreoffice --headless --convert-to pdf --outdir . preview.docx 2>&1
```

4. **尝试使用绝对路径**：
```bash
libreoffice --headless --convert-to pdf \
  --outdir /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx
```




