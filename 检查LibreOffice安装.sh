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

echo "测试文档内容" > test.txt

echo "执行: $LO_CMD --headless --convert-to pdf test.txt"
if $LO_CMD --headless --convert-to pdf test.txt 2>&1; then
    if [ -f test.pdf ]; then
        echo "✅ PDF 转换测试成功"
        ls -lh test.pdf
        rm -rf "$TEST_DIR"
    else
        echo "⚠️ 转换命令执行成功，但未找到生成的 PDF 文件"
        echo "   可能输出到了其他位置"
    fi
else
    echo "❌ PDF 转换测试失败"
    echo "   请检查 LibreOffice 是否正确安装"
    rm -rf "$TEST_DIR"
    exit 1
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

