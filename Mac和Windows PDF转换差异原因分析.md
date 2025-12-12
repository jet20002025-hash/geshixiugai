# Mac和Windows PDF转换差异原因分析

## 🔍 问题描述

同一个文档，在Mac和Windows电脑上使用LibreOffice转换后的PDF不一样。

## ⚠️ 主要原因

### 1. **字体差异**（最主要原因）

**Mac系统默认字体：**
- 中文字体：PingFang SC（苹方）、STSong（华文宋体）、STHeiti（华文黑体）
- 英文字体：Helvetica、Times New Roman

**Windows系统默认字体：**
- 中文字体：SimSun（宋体）、SimHei（黑体）、Microsoft YaHei（微软雅黑）
- 英文字体：Arial、Times New Roman

**影响：**
- 如果Word文档中使用了系统字体（如"宋体"、"黑体"），不同系统会使用不同的实际字体文件
- 字体度量（字符宽度、高度）不同，导致：
  - 文本换行位置不同
  - 页面布局不同
  - 分页位置不同

---

### 2. **LibreOffice版本差异**

不同系统上的LibreOffice版本可能不同：
- Mac: LibreOffice for Mac
- Windows: LibreOffice for Windows
- Linux: LibreOffice for Linux

不同版本的PDF生成引擎可能有细微差异。

---

### 3. **字体渲染引擎差异**

- **Mac**: 使用Core Text渲染引擎
- **Windows**: 使用GDI/GDI+渲染引擎
- **Linux**: 使用FreeType渲染引擎

不同渲染引擎对字体的处理方式不同，可能导致：
- 字符间距不同
- 行高不同
- 文本对齐方式不同

---

### 4. **PDF生成引擎差异**

LibreOffice在不同系统上可能使用不同的PDF生成后端：
- 某些版本使用内置PDF生成器
- 某些版本使用外部PDF库

---

## ✅ 解决方案

### 方案1：在Word文档中嵌入字体（推荐）

**优点：**
- 确保字体在所有系统上一致
- PDF转换时使用相同的字体文件

**实现方式：**
在Word文档中设置"嵌入字体"选项，或在代码中确保字体嵌入。

---

### 方案2：统一字体配置

**在转换前统一字体：**
1. 检测文档中使用的字体
2. 如果使用系统字体，替换为跨平台字体
3. 或使用字体映射表，将不同系统的字体映射到统一字体

**字体映射示例：**
```python
FONT_MAPPING = {
    # Mac字体 -> 统一字体
    "PingFang SC": "SimSun",  # 或使用其他跨平台字体
    "STSong": "SimSun",
    "STHeiti": "SimHei",
    # Windows字体 -> 统一字体
    "Microsoft YaHei": "SimSun",
    # 保持一致的字体
    "SimSun": "SimSun",
    "SimHei": "SimHei",
    "Times New Roman": "Times New Roman",
}
```

---

### 方案3：配置LibreOffice字体替换

**创建字体替换配置文件：**

在LibreOffice配置目录中创建字体替换规则：
- Mac: `~/Library/Application Support/LibreOffice/4/user/config/fontsubstitutions.xcu`
- Windows: `%APPDATA%\LibreOffice\4\user\config\fontsubstitutions.xcu`
- Linux: `~/.config/libreoffice/4/user/config/fontsubstitutions.xcu`

---

### 方案4：在PDF导出时嵌入字体

**LibreOffice PDF导出选项：**
- 启用"嵌入字体"选项
- 使用 `--export-pdf` 参数时添加字体嵌入选项

**命令行参数：**
```bash
libreoffice --headless --convert-to pdf:"writer_pdf_Export:{\"EmbedStandardFonts\":true}" --outdir /path/to/output input.docx
```

---

### 方案5：使用统一的字体文件

**在服务器上安装标准字体：**
1. 安装Windows字体（SimSun、SimHei等）
2. 配置LibreOffice使用这些字体
3. 确保所有转换都在同一台服务器上进行

---

## 🔧 推荐实施方案

### 短期方案（快速修复）

1. **确保所有转换在同一服务器上进行**
   - 避免跨平台差异
   - 统一字体环境

2. **在服务器上安装标准字体**
   - 安装Windows中文字体（SimSun、SimHei）
   - 配置LibreOffice使用这些字体

### 长期方案（彻底解决）

1. **在Word文档中嵌入字体**
   - 修改代码，确保字体嵌入
   - 使用跨平台字体

2. **统一字体配置**
   - 创建字体映射表
   - 在转换前统一字体

3. **PDF导出时嵌入字体**
   - 修改LibreOffice转换命令
   - 添加字体嵌入参数

---

## 📝 代码修改建议

### 1. 添加字体嵌入到PDF导出

修改 `_try_libreoffice_pdf_conversion` 函数，添加字体嵌入参数：

```python
cmd = [
    libreoffice_cmd,
    '--headless',
    '--convert-to', 'pdf:"writer_pdf_Export:{\"EmbedStandardFonts\":true,\"UseTaggedPDF\":true}"',
    '--outdir', str(output_dir),
    str(docx_path)
]
```

### 2. 在Word文档处理时统一字体

在 `_apply_rules` 函数中，确保使用统一的字体名称：
- 使用 "SimSun" 而不是 "宋体"
- 使用 "SimHei" 而不是 "黑体"
- 使用 "Times New Roman" 而不是 "Times"

---

## 🎯 检测方法

### 检查PDF中的字体

使用工具检查PDF中实际使用的字体：
```bash
# 使用 pdffonts 工具（需要安装 poppler-utils）
pdffonts output.pdf

# 或使用 Python 库
from pypdf import PdfReader
reader = PdfReader("output.pdf")
for page in reader.pages:
    if '/Font' in page.get('/Resources', {}):
        fonts = page['/Resources']['/Font']
        print(fonts)
```

### 对比两个PDF的差异

1. 提取文本内容对比
2. 检查字体使用情况
3. 检查页面布局差异

---

## ⚠️ 注意事项

1. **字体版权**：确保使用的字体有合法授权
2. **文件大小**：嵌入字体会增加PDF文件大小
3. **兼容性**：确保PDF在不同PDF阅读器上显示一致

---

## 🔍 诊断步骤

1. **检查两个系统上的字体**
   ```bash
   # Mac
   fc-list :lang=zh
   
   # Windows (PowerShell)
   Get-ChildItem "C:\Windows\Fonts" | Select-Object Name
   ```

2. **检查LibreOffice版本**
   ```bash
   libreoffice --version
   ```

3. **检查PDF中的字体**
   ```bash
   pdffonts mac_output.pdf
   pdffonts windows_output.pdf
   ```

4. **对比PDF内容**
   - 提取文本对比
   - 检查页面布局
   - 检查分页位置

---

**建议：优先在服务器上统一处理，避免跨平台差异！** 🎯

