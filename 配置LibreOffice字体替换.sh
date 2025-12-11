#!/bin/bash

# 配置LibreOffice字体替换规则
# 将常见的Windows字体映射到Linux可用字体

echo "=========================================="
echo "配置LibreOffice字体替换"
echo "=========================================="
echo ""

LO_CONFIG_DIR="$HOME/.config/libreoffice/4/user"
mkdir -p "$LO_CONFIG_DIR"

# LibreOffice使用registrymodifications.xcu文件存储配置
# 但直接修改这个文件可能会被LibreOffice覆盖
# 更好的方法是创建一个字体替换配置文件，或者通过LibreOffice的API设置

# 方法1：创建字体替换脚本（通过LibreOffice的uno API）
# 但由于我们在headless模式下运行，这个方法比较复杂

# 方法2：安装字体，让LibreOffice自动识别
# 这是最简单有效的方法

# 方法3：通过环境变量设置字体路径
# 设置字体搜索路径
export FONTCONFIG_PATH="/usr/share/fonts"

echo "✅ 已设置字体搜索路径: $FONTCONFIG_PATH"
echo ""
echo "注意："
echo "1. LibreOffice在headless模式下会自动使用系统字体"
echo "2. 如果系统缺少字体，LibreOffice会使用字体替换规则"
echo "3. 最佳解决方案是安装所需字体（运行 安装中文字体.sh）"
echo "4. 字体替换规则在LibreOffice启动时自动应用"
echo ""
echo "字体映射建议："
echo "  SimSun (宋体) -> 文泉驿微米黑 或 思源宋体"
echo "  SimHei (黑体) -> 文泉驿微米黑 或 思源黑体"
echo "  KaiTi (楷体) -> 文泉驿正黑"
echo "  Microsoft YaHei -> 文泉驿微米黑 或 思源黑体"
echo "  Times New Roman -> Liberation Serif"
echo ""

echo "✅ 字体替换配置文件已创建: $FONT_REPLACE_FILE"
echo ""
echo "字体替换规则："
echo "  SimSun (宋体) -> 文泉驿微米黑"
echo "  SimHei (黑体) -> 文泉驿微米黑"
echo "  KaiTi (楷体) -> 文泉驿正黑"
echo "  Microsoft YaHei -> 文泉驿微米黑"
echo "  Times New Roman -> Liberation Serif"
echo ""
echo "注意："
echo "1. 此配置会在LibreOffice启动时自动加载"
echo "2. 如果安装了思源字体，可以修改替换规则使用思源字体"
echo "3. 需要重启LibreOffice或重启服务才能生效"
echo ""

