#!/bin/bash

# 安装完整 LibreOffice 的脚本

echo "=========================================="
echo "安装完整 LibreOffice"
echo "=========================================="
echo ""

# 1. 检查已安装的 LibreOffice 包
echo "1. 检查已安装的 LibreOffice 包..."
echo "----------------------------------------"
rpm -qa | grep -i libreoffice
echo "----------------------------------------"
echo ""

# 2. 检查可用的 LibreOffice 包
echo "2. 检查可用的 LibreOffice 包..."
echo "----------------------------------------"
yum list available | grep -i libreoffice | head -n 20
echo "----------------------------------------"
echo ""

# 3. 尝试安装完整的 LibreOffice
echo "3. 尝试安装完整的 LibreOffice..."
echo "----------------------------------------"

# 检测操作系统类型
OS_TYPE=$(cat /etc/os-release | grep "^ID=" | cut -d'=' -f2 | tr -d '"')
echo "检测到操作系统: $OS_TYPE"

if [[ "$OS_TYPE" == "alinux" ]] || [[ "$OS_TYPE" == "centos" ]] || [[ "$OS_TYPE" == "rhel" ]]; then
    echo "使用 yum 安装..."
    
    # 尝试安装完整的 LibreOffice
    echo "尝试安装: libreoffice"
    sudo yum install -y libreoffice 2>&1 | tail -n 10
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "尝试安装: libreoffice-core"
        sudo yum install -y libreoffice-core 2>&1 | tail -n 10
    fi
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "尝试安装: libreoffice-writer（包含 PDF 导出功能）"
        sudo yum install -y libreoffice-writer 2>&1 | tail -n 10
    fi
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "尝试安装所有 LibreOffice 相关包..."
        sudo yum install -y libreoffice* 2>&1 | tail -n 20
    fi
elif [[ "$OS_TYPE" == "ubuntu" ]] || [[ "$OS_TYPE" == "debian" ]]; then
    echo "使用 apt 安装..."
    sudo apt update
    sudo apt install -y libreoffice 2>&1 | tail -n 10
else
    echo "⚠️ 不支持的操作系统: $OS_TYPE"
    echo "请手动安装 LibreOffice"
fi

echo "----------------------------------------"
echo ""

# 4. 验证安装
echo "4. 验证 LibreOffice 安装..."
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
else
    echo "❌ PDF 转换失败"
    echo "错误信息："
    libreoffice --headless --convert-to pdf --outdir "$TEMP_DIR" "$TEMP_DIR/test.txt" 2>&1
fi

# 清理
rm -rf "$TEMP_DIR"
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "安装完成"
echo "=========================================="
echo ""



