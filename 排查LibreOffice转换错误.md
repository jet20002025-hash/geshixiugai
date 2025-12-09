# 排查 LibreOffice 转换错误

## 🔍 错误：source file could not be loaded

这个错误可能的原因：

1. **文件路径问题**：路径不正确或文件不存在
2. **文件权限问题**：LibreOffice 无法读取文件
3. **文件损坏**：DOCX 文件可能损坏
4. **LibreOffice 配置问题**：需要额外的参数

## 📋 排查步骤

### 步骤1: 检查文件是否存在

```bash
# 检查文件是否存在
ls -lh /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 检查文件类型
file /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 检查文件权限
ls -l /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx
```

### 步骤2: 尝试进入文档目录执行

```bash
# 进入文档目录
cd /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc

# 检查文件
ls -lh preview.docx

# 使用相对路径执行
libreoffice --headless --convert-to pdf --outdir . preview.docx
```

### 步骤3: 检查 LibreOffice 是否能正常启动

```bash
# 测试 LibreOffice 是否正常
libreoffice --version

# 尝试打开一个简单的文件
echo "test" > /tmp/test.txt
libreoffice --headless --convert-to pdf --outdir /tmp /tmp/test.txt
ls -lh /tmp/test.pdf
```

### 步骤4: 尝试使用不同的参数

```bash
# 方法1: 添加更多参数
libreoffice --headless --invisible --nodefault --nolockcheck \
  --convert-to pdf --outdir /tmp \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 方法2: 先复制到临时目录
cp /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx /tmp/test.docx
cd /tmp
libreoffice --headless --convert-to pdf test.docx
ls -lh test.pdf
```

### 步骤5: 检查文件是否损坏

```bash
# 尝试用 python-docx 打开文件（如果安装了）
python3 -c "from docx import Document; doc = Document('/var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx'); print('文件可以正常打开')"
```

### 步骤6: 检查 LibreOffice 日志

```bash
# 启用详细日志
libreoffice --headless --convert-to pdf --outdir /tmp \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx \
  2>&1 | tee /tmp/libreoffice.log

# 查看日志
cat /tmp/libreoffice.log
```

## 💡 可能的解决方案

### 方案1: 使用 original.docx 而不是 preview.docx

```bash
# 尝试转换 original.docx
libreoffice --headless --convert-to pdf --outdir /tmp \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/original.docx
```

### 方案2: 检查文件大小

```bash
# 如果文件大小为0或异常小，可能有问题
ls -lh /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/*.docx
```

### 方案3: 尝试其他文档

```bash
# 找一个其他的文档测试
ls -t /var/www/geshixiugai/storage/documents/*/preview.docx | head -3

# 使用最新的文档测试
LATEST_DOC=$(ls -t /var/www/geshixiugai/storage/documents/*/preview.docx | head -1 | xargs dirname)
cd $LATEST_DOC
libreoffice --headless --convert-to pdf --outdir . preview.docx
```

## 🐛 如果所有方法都失败

如果所有方法都失败，可能是：

1. **LibreOffice 安装不完整**：需要重新安装
2. **文件格式问题**：DOCX 文件可能使用了 LibreOffice 不支持的格式
3. **系统依赖缺失**：缺少必要的库

请执行以上步骤，并把结果发给我，我会根据实际情况继续修复。

