#!/bin/bash

# 检查服务器上的字体安装情况

echo "=========================================="
echo "检查服务器字体安装情况"
echo "=========================================="
echo ""

# 1. 检查系统字体目录
echo "1. 系统字体目录："
echo "----------------------------------------"
ls -la /usr/share/fonts/ 2>/dev/null | head -n 20
echo ""

# 2. 检查中文字体
echo "2. 已安装的中文字体："
echo "----------------------------------------"
fc-list :lang=zh 2>/dev/null | head -n 30
echo ""

# 3. 检查常见中文字体
echo "3. 检查常见中文字体："
echo "----------------------------------------"
for font in "SimSun" "SimHei" "KaiTi" "Microsoft YaHei" "Times New Roman"; do
    if fc-list | grep -i "$font" > /dev/null 2>&1; then
        echo "✅ $font: 已安装"
        fc-list | grep -i "$font" | head -n 1
    else
        echo "❌ $font: 未安装"
    fi
    echo ""
done

# 4. 检查所有可用字体数量
echo "4. 字体统计："
echo "----------------------------------------"
total_fonts=$(fc-list 2>/dev/null | wc -l)
chinese_fonts=$(fc-list :lang=zh 2>/dev/null | wc -l)
echo "总字体数: $total_fonts"
echo "中文字体数: $chinese_fonts"
echo ""

# 5. 检查LibreOffice字体配置
echo "5. LibreOffice字体配置目录："
echo "----------------------------------------"
if [ -d "$HOME/.config/libreoffice" ]; then
    echo "用户配置目录: $HOME/.config/libreoffice"
    ls -la "$HOME/.config/libreoffice" 2>/dev/null | head -n 10
else
    echo "未找到用户配置目录"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果缺少字体，请安装相应的字体文件到 /usr/share/fonts/"
echo "安装后运行: sudo fc-cache -fv"
echo ""

