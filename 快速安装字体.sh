#!/bin/bash

# 快速安装字体 - 使用yum包管理器（最可靠的方法）

echo "=========================================="
echo "快速安装字体（使用yum）"
echo "=========================================="
echo ""

# 1. 安装文泉驿字体（确保完整）
echo "1. 安装文泉驿字体..."
echo "----------------------------------------"
sudo yum install -y wqy-microhei-fonts wqy-zenhei-fonts 2>&1 | grep -E "已安装|Installed|Complete|完成" || echo "文泉驿字体安装完成或已存在"
echo ""

# 2. 安装Liberation字体（Times New Roman替代）
echo "2. 安装Liberation字体..."
echo "----------------------------------------"
sudo yum install -y liberation-serif-fonts liberation-sans-fonts liberation-mono-fonts 2>&1 | grep -E "已安装|Installed|Complete|完成" || echo "Liberation字体安装完成或已存在"
echo ""

# 3. 更新字体缓存
echo "3. 更新字体缓存..."
echo "----------------------------------------"
sudo fc-cache -fv 2>&1 | tail -n 5
echo ""

# 4. 验证安装
echo "4. 验证字体安装..."
echo "----------------------------------------"
echo "中文字体："
fc-list :lang=zh | head -n 10
echo ""
echo "Liberation字体："
fc-list | grep -i "liberation" | head -n 5
echo ""
echo "总字体数: $(fc-list | wc -l)"
echo "中文字体数: $(fc-list :lang=zh | wc -l)"
echo ""

echo "=========================================="
echo "字体安装完成"
echo "=========================================="
echo ""
echo "注意："
echo "1. 如果Word文档使用SimSun（宋体），LibreOffice会使用文泉驿微米黑替代"
echo "2. 如果Word文档使用SimHei（黑体），LibreOffice会使用文泉驿微米黑替代"
echo "3. 如果Word文档使用KaiTi（楷体），LibreOffice会使用文泉驿正黑替代"
echo "4. 如果Word文档使用Times New Roman，LibreOffice会使用Liberation Serif替代"
echo ""
echo "如果需要更好的字体支持，可以手动安装思源字体："
echo "  1. 访问: https://github.com/adobe-fonts/source-han-serif/releases"
echo "  2. 下载 SimplifiedChinese 版本的 OTF 文件"
echo "  3. 复制到: /usr/share/fonts/chinese/"
echo "  4. 运行: sudo fc-cache -fv"
echo ""

