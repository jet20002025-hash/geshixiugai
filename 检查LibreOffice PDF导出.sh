#!/bin/bash

# 检查 LibreOffice PDF 导出功能的脚本

echo "=========================================="
echo "检查 LibreOffice PDF 导出功能"
echo "=========================================="
echo ""

# 1. 检查 LibreOffice 版本
echo "1. 检查 LibreOffice 版本..."
libreoffice --version 2>&1
echo ""

# 2. 检查 LibreOffice 是否支持 PDF 导出
echo "2. 检查 LibreOffice PDF 导出过滤器..."
# 查找 PDF 导出过滤器
if [ -d "/usr/lib64/libreoffice" ]; then
    echo "检查 /usr/lib64/libreoffice..."
    find /usr/lib64/libreoffice -name "*pdf*" -type f 2>/dev/null | head -n 10
fi
if [ -d "/usr/lib/libreoffice" ]; then
    echo "检查 /usr/lib/libreoffice..."
    find /usr/lib/libreoffice -name "*pdf*" -type f 2>/dev/null | head -n 10
fi
echo ""

# 3. 测试 PDF 转换（使用简单的文本文件）
echo "3. 测试 PDF 转换功能..."
TEMP_DIR=$(mktemp -d)
TEMP_DOC="$TEMP_DIR/test.docx"
TEMP_PDF="$TEMP_DIR/test.pdf"

# 创建一个简单的测试文档（如果可能）
echo "测试转换..."
# 尝试转换一个不存在的文件，看看错误信息
libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" /nonexistent/test.docx 2>&1 | head -n 5
echo ""

# 4. 检查 LibreOffice 的配置
echo "4. 检查 LibreOffice 配置..."
if [ -d "$HOME/.config/libreoffice" ]; then
    echo "用户配置目录: $HOME/.config/libreoffice"
    ls -la "$HOME/.config/libreoffice" 2>/dev/null | head -n 5
else
    echo "用户配置目录不存在"
fi
echo ""

# 5. 检查是否缺少组件
echo "5. 检查 LibreOffice 组件..."
rpm -qa | grep -i libreoffice | head -n 10
echo ""

# 6. 尝试手动测试转换
echo "6. 手动测试转换..."
echo "创建一个测试文件..."
cat > "$TEMP_DIR/test.txt" << EOF
这是一个测试文档
This is a test document
EOF

echo "尝试转换为 PDF..."
libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_DIR/test.txt" 2>&1

if [ -f "$TEMP_DIR/test.pdf" ]; then
    echo "✅ PDF 转换成功！"
    ls -lh "$TEMP_DIR/test.pdf"
else
    echo "❌ PDF 转换失败"
    echo "错误信息："
    libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_DIR/test.txt" 2>&1
fi

# 清理
rm -rf "$TEMP_DIR"
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果 PDF 转换失败，可能需要："
echo "1. 安装完整的 LibreOffice: sudo yum install -y libreoffice"
echo "2. 或者安装 PDF 导出组件: sudo yum install -y libreoffice-pdfimport"
echo ""

