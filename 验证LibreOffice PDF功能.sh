#!/bin/bash

# 验证 LibreOffice PDF 功能的脚本

echo "=========================================="
echo "验证 LibreOffice PDF 功能"
echo "=========================================="
echo ""

# 1. 检查已安装的 LibreOffice 包
echo "1. 检查已安装的 LibreOffice 包..."
echo "----------------------------------------"
rpm -qa | grep -i libreoffice | sort
echo "----------------------------------------"
echo ""

# 2. 检查 LibreOffice 命令
echo "2. 检查 LibreOffice 命令..."
echo "----------------------------------------"
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice 命令可用: $(which libreoffice)"
    libreoffice --version 2>&1 | head -n 1
else
    echo "❌ LibreOffice 命令不可用"
fi
echo ""

if command -v soffice &> /dev/null; then
    echo "✅ soffice 命令可用: $(which soffice)"
    soffice --version 2>&1 | head -n 1
else
    echo "❌ soffice 命令不可用"
fi
echo "----------------------------------------"
echo ""

# 3. 检查 PDF 导出过滤器
echo "3. 检查 PDF 导出过滤器..."
echo "----------------------------------------"
if [ -d "/usr/lib64/libreoffice" ]; then
    echo "查找 PDF 导出过滤器..."
    PDF_FILTERS=$(find /usr/lib64/libreoffice -name "*pdf*" -type f 2>/dev/null | grep -iE "filter|export" | head -n 10)
    if [ -n "$PDF_FILTERS" ]; then
        echo "✅ 找到 PDF 导出过滤器："
        echo "$PDF_FILTERS"
    else
        echo "⚠️ 未找到 PDF 导出过滤器"
    fi
fi
echo "----------------------------------------"
echo ""

# 4. 测试 PDF 转换（使用 .doc 文件）
echo "4. 测试 PDF 转换功能（使用 .doc 文件）..."
echo "----------------------------------------"
TEMP_DIR=$(mktemp -d)
TEMP_DOC="$TEMP_DIR/test.doc"

# 创建一个简单的测试 Word 文档（使用 echo 创建基本内容）
cat > "$TEMP_DOC" << 'EOF'
这是一个测试文档
This is a test document
EOF

echo "尝试将 .doc 文件转换为 PDF..."
libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_DOC" 2>&1

if [ -f "$TEMP_DIR/test.pdf" ]; then
    echo "✅ PDF 转换成功！"
    ls -lh "$TEMP_DIR/test.pdf"
    echo "PDF 文件大小: $(stat -c%s "$TEMP_DIR/test.pdf") bytes"
    rm -f "$TEMP_DIR/test.pdf"
else
    echo "❌ PDF 转换失败"
    echo "详细错误信息："
    libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_DOC" 2>&1
    echo ""
    echo "检查输出目录中的文件："
    ls -lah "$TEMP_DIR/"
fi

# 清理
rm -rf "$TEMP_DIR"
echo "----------------------------------------"
echo ""

# 5. 测试 PDF 转换（使用 .txt 文件）
echo "5. 测试 PDF 转换功能（使用 .txt 文件）..."
echo "----------------------------------------"
TEMP_DIR=$(mktemp -d)
TEMP_TXT="$TEMP_DIR/test.txt"

cat > "$TEMP_TXT" << 'EOF'
Test Document
测试文档
EOF

echo "尝试将 .txt 文件转换为 PDF..."
libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_TXT" 2>&1

if [ -f "$TEMP_DIR/test.pdf" ]; then
    echo "✅ PDF 转换成功！"
    ls -lh "$TEMP_DIR/test.pdf"
    echo "PDF 文件大小: $(stat -c%s "$TEMP_DIR/test.pdf") bytes"
    rm -f "$TEMP_DIR/test.pdf"
else
    echo "❌ PDF 转换失败"
    echo "详细错误信息："
    libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_TXT" 2>&1
fi

# 清理
rm -rf "$TEMP_DIR"
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "验证完成"
echo "=========================================="
echo ""
echo "如果 PDF 转换成功，说明 LibreOffice PDF 功能正常。"
echo "如果仍然失败，可能需要重启服务或检查其他配置。"
echo ""



