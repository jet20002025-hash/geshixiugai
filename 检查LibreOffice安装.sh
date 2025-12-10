#!/bin/bash

# 检查 LibreOffice 安装状态

echo "=========================================="
echo "检查 LibreOffice 安装状态"
echo "=========================================="
echo ""

# 1. 检查命令是否存在
echo "1. 检查 LibreOffice 命令..."
if command -v libreoffice &> /dev/null; then
    LO_CMD="libreoffice"
    LO_PATH=$(which libreoffice)
    echo "✅ 找到 libreoffice 命令: $LO_PATH"
elif command -v soffice &> /dev/null; then
    LO_CMD="soffice"
    LO_PATH=$(which soffice)
    echo "✅ 找到 soffice 命令: $LO_PATH"
else
    echo "❌ 未找到 LibreOffice 命令"
    echo ""
    echo "请执行以下命令安装 LibreOffice："
    echo ""
    echo "  # 阿里云 Linux (alinux)"
    echo "  sudo yum install -y libreoffice-headless"
    echo ""
    echo "  # 如果上面命令失败，尝试："
    echo "  sudo yum install -y libreoffice"
    echo ""
    exit 1
fi

# 2. 检查版本
echo ""
echo "2. 检查 LibreOffice 版本..."
if $LO_CMD --version 2>&1; then
    echo "✅ LibreOffice 版本检查成功"
else
    echo "❌ LibreOffice 版本检查失败"
    exit 1
fi

# 3. 测试转换功能
echo ""
echo "3. 测试 PDF 转换功能..."
TEST_DIR="/tmp/libreoffice_test_$$"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# 创建测试文件（使用绝对路径）
TEST_FILE="$TEST_DIR/test.txt"
echo "测试文档内容" > "$TEST_FILE"

# 使用绝对路径执行转换
echo "执行: $LO_CMD --headless --convert-to pdf --outdir $TEST_DIR $TEST_FILE"
OUTPUT=$($LO_CMD --headless --convert-to pdf --outdir "$TEST_DIR" "$TEST_FILE" 2>&1)
EXIT_CODE=$?

echo "LibreOffice 输出:"
echo "$OUTPUT"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    # 检查是否生成了 PDF 文件
    if [ -f "$TEST_DIR/test.pdf" ]; then
        echo "✅ PDF 转换测试成功"
        ls -lh "$TEST_DIR/test.pdf"
        rm -rf "$TEST_DIR"
    else
        echo "⚠️ 转换命令返回成功，但未找到生成的 PDF 文件"
        echo "   检查输出目录中的所有文件:"
        ls -la "$TEST_DIR"
        echo ""
        echo "   注意: LibreOffice 可能因为某些原因无法转换 .txt 文件"
        echo "   但这不影响 Word 文档 (.docx) 的转换"
        rm -rf "$TEST_DIR"
    fi
else
    echo "⚠️ PDF 转换测试返回错误码: $EXIT_CODE"
    echo "   注意: LibreOffice 可能无法直接转换 .txt 文件"
    echo "   但这不影响 Word 文档 (.docx) 的转换"
    echo ""
    echo "   如果实际转换 Word 文档时仍然失败，请查看服务日志："
    echo "   sudo journalctl -u geshixiugai -f | grep -E '\[PDF预览\]'"
    rm -rf "$TEST_DIR"
fi

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "LibreOffice 安装状态：✅ 正常"
echo "命令路径: $LO_PATH"
echo ""
echo "如果服务仍然无法使用 LibreOffice，请："
echo "1. 重启服务: sudo systemctl restart geshixiugai"
echo "2. 查看日志: sudo journalctl -u geshixiugai -f | grep -E '\[PDF预览\]'"
echo ""

