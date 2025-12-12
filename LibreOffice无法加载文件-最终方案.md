# LibreOffice 无法加载文件 - 最终方案

## 🔍 问题确认

即使复制到临时目录，LibreOffice 仍然无法加载文件。这说明：
1. 不是权限问题
2. 不是路径问题
3. 可能是 LibreOffice 无法读取这个特定的 DOCX 文件
4. 或者 LibreOffice 安装有问题

## 📋 诊断步骤

### 步骤1: 测试 LibreOffice 是否正常工作

```bash
# 创建一个简单的测试文件
echo "test" > /tmp/test.txt

# 尝试转换文本文件
libreoffice --headless --convert-to pdf /tmp/test.txt

# 检查结果
ls -lh /tmp/test.pdf
```

### 步骤2: 检查 DOCX 文件是否有效

```bash
# 尝试用 python-docx 打开
python3 -c "
from docx import Document
try:
    doc = Document('/tmp/test.docx')
    print('✅ 文件可以正常打开')
    print('段落数:', len(doc.paragraphs))
except Exception as e:
    print('❌ 文件打开失败:', e)
"
```

### 步骤3: 检查 LibreOffice 版本和配置

```bash
# 检查版本
libreoffice --version

# 检查 LibreOffice 是否能正常启动
libreoffice --headless --version

# 检查依赖
ldd $(which libreoffice) | head -20
```

## 💡 解决方案

### 方案1: 如果 LibreOffice 本身有问题

如果连简单的文本文件都无法转换，说明 LibreOffice 安装有问题，需要：
1. 重新安装 LibreOffice
2. 或者使用其他转换工具

### 方案2: 如果只是这个 DOCX 文件有问题

如果 LibreOffice 可以转换其他文件，只是这个 DOCX 有问题，可以：
1. 尝试转换 original.docx
2. 或者回退到 WeasyPrint（需要解决 transform 错误）
3. 或者改进 HTML 预览

### 方案3: 回退到 WeasyPrint（推荐）

由于 LibreOffice 一直无法正常工作，建议：
1. **回退到 WeasyPrint**，但需要解决 transform 错误
2. 或者**改进 HTML 预览**，让它更接近 Word

## 🚀 推荐方案：修复 WeasyPrint transform 错误

既然 LibreOffice 无法正常工作，我们应该专注于修复 WeasyPrint 的 transform 错误。

可能的解决方案：
1. 降级 WeasyPrint 到更稳定的版本
2. 降级 pypdf 到兼容版本
3. 或者完全移除有问题的 CSS 属性

## 📝 下一步

请执行步骤1（测试 LibreOffice 是否能转换简单的文本文件），然后告诉我结果。

如果 LibreOffice 连文本文件都无法转换，说明安装有问题，我们应该：
1. 回退到 WeasyPrint
2. 或者重新安装 LibreOffice

如果 LibreOffice 可以转换文本文件，但无法转换 DOCX，可能是 DOCX 文件格式问题，我们可以：
1. 尝试转换 original.docx
2. 或者回退到 WeasyPrint




