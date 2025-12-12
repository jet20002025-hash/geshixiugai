#!/bin/bash

# 安装 LibreOffice PDF 导出功能的脚本

echo "=========================================="
echo "安装 LibreOffice PDF 导出功能"
echo "=========================================="
echo ""

# 1. 检查已安装的 LibreOffice 包
echo "1. 检查已安装的 LibreOffice 包..."
echo "----------------------------------------"
rpm -qa | grep -i libreoffice | sort
echo "----------------------------------------"
echo ""

# 2. 检查可用的 LibreOffice 包（特别是 PDF 相关）
echo "2. 检查可用的 LibreOffice PDF 相关包..."
echo "----------------------------------------"
yum list available | grep -iE "libreoffice.*pdf|libreoffice.*writer|libreoffice.*calc" | head -n 20
echo "----------------------------------------"
echo ""

# 3. 尝试安装 PDF 导出相关的包
echo "3. 尝试安装 PDF 导出相关的包..."
echo "----------------------------------------"

# 尝试安装 libreoffice-writer（包含 PDF 导出功能）
echo "尝试安装: libreoffice-writer"
sudo yum install -y libreoffice-writer 2>&1 | tail -n 15

if [ $? -ne 0 ]; then
    echo ""
    echo "尝试安装: libreoffice-writer-core"
    sudo yum install -y libreoffice-writer-core 2>&1 | tail -n 15
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "尝试安装所有可用的 LibreOffice 组件（跳过冲突的包）..."
    sudo yum install -y libreoffice* --skip-broken 2>&1 | tail -n 20
fi

echo "----------------------------------------"
echo ""

# 4. 检查 PDF 导出过滤器
echo "4. 检查 PDF 导出过滤器..."
echo "----------------------------------------"
if [ -d "/usr/lib64/libreoffice" ]; then
    echo "查找 PDF 导出过滤器..."
    find /usr/lib64/libreoffice -name "*pdf*" -type f 2>/dev/null | grep -iE "filter|export" | head -n 10
fi
if [ -d "/usr/lib/libreoffice" ]; then
    echo "查找 PDF 导出过滤器..."
    find /usr/lib/libreoffice -name "*pdf*" -type f 2>/dev/null | grep -iE "filter|export" | head -n 10
fi
echo "----------------------------------------"
echo ""

# 5. 测试 PDF 转换
echo "5. 测试 PDF 转换功能..."
echo "----------------------------------------"
TEMP_DIR=$(mktemp -d)
TEMP_DOC="$TEMP_DIR/test.docx"

# 创建一个简单的测试文档
cat > "$TEMP_DIR/test.txt" << EOF
Test Document
测试文档
EOF

echo "尝试转换为 PDF..."
libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_DIR/test.txt" 2>&1

if [ -f "$TEMP_DIR/test.pdf" ]; then
    echo "✅ PDF 转换成功！"
    ls -lh "$TEMP_DIR/test.pdf"
    rm -f "$TEMP_DIR/test.pdf"
else
    echo "❌ PDF 转换失败"
    echo "详细错误信息："
    libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_DIR/test.txt" 2>&1
fi

# 清理
rm -rf "$TEMP_DIR"
echo "----------------------------------------"
echo ""

# 6. 检查 LibreOffice 版本和功能
echo "6. 检查 LibreOffice 版本和功能..."
echo "----------------------------------------"
libreoffice --version 2>&1
echo ""
echo "检查 LibreOffice 支持的文件格式..."
libreoffice --headless --help 2>&1 | grep -iE "convert|filter" | head -n 10
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果 PDF 转换仍然失败，可能需要："
echo "1. 安装完整的 LibreOffice: sudo yum install -y libreoffice-writer libreoffice-calc"
echo "2. 或者检查是否有其他 PDF 导出相关的包"
echo ""



