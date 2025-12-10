#!/bin/bash

# LibreOffice 服务器安装脚本（适用于阿里云 Linux 服务器）

echo "=========================================="
echo "LibreOffice 安装脚本（阿里云服务器）"
echo "=========================================="
echo ""

# 检测操作系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
else
    echo "❌ 无法检测操作系统类型"
    exit 1
fi

echo "检测到操作系统: $OS $OS_VERSION"
echo ""

# 检查是否已安装
echo "🔍 检查 LibreOffice 是否已安装..."
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice 已安装"
    libreoffice --version
    echo ""
    echo "安装路径: $(which libreoffice)"
    exit 0
fi

if command -v soffice &> /dev/null; then
    echo "✅ LibreOffice (soffice) 已安装"
    soffice --version
    echo ""
    echo "安装路径: $(which soffice)"
    exit 0
fi

echo "❌ LibreOffice 未安装，开始安装..."
echo ""

# 根据操作系统类型安装
case $OS in
    "centos"|"rhel"|"almalinux"|"rocky")
        echo "📦 使用 yum 安装 LibreOffice (CentOS/RHEL/Alibaba Cloud Linux)..."
        echo ""
        
        # 尝试安装 headless 版本（更轻量）
        if sudo yum install -y libreoffice-headless 2>&1 | tee /tmp/libreoffice_install.log; then
            echo ""
            echo "✅ LibreOffice 安装成功"
        else
            echo ""
            echo "⚠️ libreoffice-headless 安装失败，尝试安装完整版..."
            if sudo yum install -y libreoffice 2>&1 | tee -a /tmp/libreoffice_install.log; then
                echo ""
                echo "✅ LibreOffice 安装成功"
            else
                echo ""
                echo "❌ LibreOffice 安装失败"
                echo "请查看日志: /tmp/libreoffice_install.log"
                exit 1
            fi
        fi
        ;;
    
    "ubuntu"|"debian")
        echo "📦 使用 apt 安装 LibreOffice (Ubuntu/Debian)..."
        echo ""
        
        # 更新软件包列表
        sudo apt update
        
        # 安装 LibreOffice（无推荐依赖，减少体积）
        if sudo apt install -y libreoffice --no-install-recommends 2>&1 | tee /tmp/libreoffice_install.log; then
            echo ""
            echo "✅ LibreOffice 安装成功"
        else
            echo ""
            echo "❌ LibreOffice 安装失败"
            echo "请查看日志: /tmp/libreoffice_install.log"
            exit 1
        fi
        ;;
    
    *)
        echo "❌ 不支持的操作系统: $OS"
        echo "请手动安装 LibreOffice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "验证安装"
echo "=========================================="

# 验证安装
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice 命令可用: $(which libreoffice)"
    libreoffice --version
elif command -v soffice &> /dev/null; then
    echo "✅ LibreOffice (soffice) 命令可用: $(which soffice)"
    soffice --version
else
    echo "❌ LibreOffice 安装后仍无法找到命令"
    echo "请检查 PATH 环境变量"
    exit 1
fi

echo ""
echo "=========================================="
echo "测试转换功能"
echo "=========================================="

# 创建测试文件
TEST_DIR="/tmp/libreoffice_test_$$"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "测试文档内容" > test.txt

# 测试转换
LO_CMD=""
if command -v libreoffice &> /dev/null; then
    LO_CMD="libreoffice"
elif command -v soffice &> /dev/null; then
    LO_CMD="soffice"
fi

if [ -n "$LO_CMD" ]; then
    echo "执行测试转换: $LO_CMD --headless --convert-to pdf test.txt"
    if $LO_CMD --headless --convert-to pdf test.txt 2>&1; then
        if [ -f test.pdf ]; then
            echo "✅ PDF 转换测试成功"
            ls -lh test.pdf
            rm -rf "$TEST_DIR"
        else
            echo "⚠️ 转换命令执行成功，但未找到生成的 PDF 文件"
        fi
    else
        echo "⚠️ PDF 转换测试失败（可能不影响基本功能）"
    fi
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 重启服务: sudo systemctl restart geshixiugai"
echo "2. 查看日志: sudo journalctl -u geshixiugai -f | grep -E '\[PDF预览\]'"
echo "3. 测试转换: 访问 https://www.geshixiugai.cn/web/convert.html"
echo ""

