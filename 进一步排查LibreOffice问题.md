# 进一步排查 LibreOffice 问题

## 🔍 问题：即使以 nginx 用户运行也失败

说明不是权限问题，可能是：
1. LibreOffice 无法读取这个特定的 DOCX 文件
2. 文件格式问题
3. LibreOffice 配置问题

## 📋 测试步骤

### 步骤1: 测试方案2（复制到临时目录）

```bash
# 复制到临时目录
sudo cp /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx /tmp/test.docx

# 转换
cd /tmp
libreoffice --headless --convert-to pdf test.docx

# 检查结果
ls -lh test.pdf
```

### 步骤2: 尝试转换 original.docx

```bash
# 尝试转换 original.docx（可能 preview.docx 有问题）
cd /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc
sudo -u nginx libreoffice --headless --convert-to pdf --outdir . original.docx
ls -lh original.pdf
```

### 步骤3: 检查 LibreOffice 详细错误

```bash
# 启用详细输出
sudo -u nginx libreoffice --headless --convert-to pdf \
  --outdir /tmp \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx \
  2>&1 | tee /tmp/libreoffice_error.log

# 查看详细错误
cat /tmp/libreoffice_error.log
```

### 步骤4: 尝试使用不同的参数

```bash
# 方法1: 添加更多参数
sudo -u nginx libreoffice --headless --invisible --nodefault --nolockcheck \
  --convert-to pdf --outdir /tmp \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 方法2: 使用相对路径（在文档目录中）
cd /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc
sudo -u nginx libreoffice --headless --convert-to pdf --outdir . preview.docx
```

### 步骤5: 检查文件是否真的可以读取

```bash
# 尝试用 python-docx 打开（如果安装了）
python3 -c "
from docx import Document
try:
    doc = Document('/var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx')
    print('✅ 文件可以正常打开，段落数:', len(doc.paragraphs))
except Exception as e:
    print('❌ 文件打开失败:', e)
"
```

### 步骤6: 尝试其他文档

```bash
# 找一个其他的文档测试
ls -t /var/www/geshixiugai/storage/documents/*/preview.docx | head -3

# 使用最新的文档测试
LATEST_DOC=$(ls -t /var/www/geshixiugai/storage/documents/*/preview.docx | head -1 | xargs dirname)
cd $LATEST_DOC
sudo -u nginx libreoffice --headless --convert-to pdf --outdir . preview.docx
ls -lh preview.pdf
```

## 💡 可能的解决方案

### 如果方案2（复制到临时目录）成功

说明 LibreOffice 可以工作，问题在于文件路径或权限。可能需要：
1. 在代码中先复制文件到临时目录
2. 转换后再复制回原目录

### 如果所有方法都失败

可能需要：
1. 重新安装 LibreOffice
2. 使用其他转换工具（如 unoconv）
3. 回退到 WeasyPrint（但需要解决 transform 错误）

## 🐛 如果文件确实有问题

如果这个特定的 DOCX 文件无法转换，但其他文件可以，可能需要：
1. 检查文件是否损坏
2. 尝试重新生成 preview.docx
3. 使用 original.docx 代替

请先执行步骤1和步骤2，看看结果如何。




