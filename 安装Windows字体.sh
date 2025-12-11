#!/bin/bash

# 安装Windows字体到Linux服务器
# 从Windows系统的C:\Windows\Fonts目录复制字体文件

echo "=========================================="
echo "安装Windows字体到Linux服务器"
echo "=========================================="
echo ""
echo "此脚本用于安装Windows字体文件到Linux服务器"
echo "需要从Windows系统的 C:\\Windows\\Fonts 目录获取字体文件"
echo ""

FONT_DIR="/usr/share/fonts/chinese"
sudo mkdir -p "$FONT_DIR"

echo "字体文件安装说明："
echo "----------------------------------------"
echo ""
echo "1. 从Windows系统获取字体文件："
echo "   位置: C:\\Windows\\Fonts"
echo "   需要的字体文件："
echo "   - simsun.ttc (宋体)"
echo "   - simhei.ttf (黑体)"
echo "   - kaiu.ttf (楷体)"
echo "   - times.ttf 或 timesnr.ttf (Times New Roman)"
echo ""
echo "2. 上传字体文件到服务器："
echo "   可以使用 scp 命令："
echo "   scp C:\\Windows\\Fonts\\simsun.ttc user@server:/tmp/"
echo "   scp C:\\Windows\\Fonts\\simhei.ttf user@server:/tmp/"
echo "   scp C:\\Windows\\Fonts\\kaiu.ttf user@server:/tmp/"
echo "   scp C:\\Windows\\Fonts\\times.ttf user@server:/tmp/"
echo ""
echo "3. 在服务器上运行此脚本安装字体："
echo "   sudo ./安装Windows字体.sh"
echo ""
echo "=========================================="
echo "检查临时目录中的字体文件"
echo "=========================================="
echo ""

# 检查/tmp目录中的字体文件
FONTS_INSTALLED=0

for font_file in /tmp/simsun.ttc /tmp/simhei.ttf /tmp/kaiu.ttf /tmp/times.ttf /tmp/timesnr.ttf; do
    if [ -f "$font_file" ]; then
        font_name=$(basename "$font_file")
        echo "发现字体文件: $font_name"
        sudo cp "$font_file" "$FONT_DIR/"
        echo "✅ 已安装: $font_name"
        FONTS_INSTALLED=1
    fi
done

if [ $FONTS_INSTALLED -eq 0 ]; then
    echo "⚠️  未在/tmp目录找到字体文件"
    echo ""
    echo "请按照以下步骤操作："
    echo "1. 从Windows系统复制字体文件到/tmp目录"
    echo "2. 然后重新运行此脚本"
    echo ""
    echo "或者手动安装："
    echo "   sudo cp /path/to/font.ttf $FONT_DIR/"
    echo "   sudo fc-cache -fv"
else
    echo ""
    echo "更新字体缓存..."
    sudo fc-cache -fv
    echo ""
    echo "验证安装..."
    echo "中文字体："
    fc-list :lang=zh | head -n 10
    echo ""
    echo "Times New Roman："
    fc-list | grep -i "times" | head -n 5
    echo ""
    echo "✅ 字体安装完成！"
    echo ""
    echo "注意：安装后需要重启LibreOffice或重启服务才能生效"
fi

echo ""

