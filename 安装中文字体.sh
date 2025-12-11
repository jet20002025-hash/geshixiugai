#!/bin/bash

# 安装常见中文字体和英文字体
# 使用开源字体，避免版权问题

echo "=========================================="
echo "安装中文字体和英文字体"
echo "=========================================="
echo ""

FONT_DIR="/usr/share/fonts/chinese"
mkdir -p "$FONT_DIR"

# 1. 安装思源字体（开源，支持中文）
echo "1. 检查并安装思源字体..."
echo "----------------------------------------"

# 思源宋体
if [ ! -f "$FONT_DIR/SourceHanSerifSC-Regular.otf" ]; then
    echo "下载思源宋体..."
    cd /tmp
    wget -q https://github.com/adobe-fonts/source-han-serif/raw/release/OTF/SimplifiedChinese/SourceHanSerifSC-Regular.otf -O SourceHanSerifSC-Regular.otf 2>/dev/null || {
        echo "⚠️  无法从GitHub下载思源宋体，请手动下载并安装"
        echo "   下载地址: https://github.com/adobe-fonts/source-han-serif/releases"
    }
    if [ -f "SourceHanSerifSC-Regular.otf" ]; then
        sudo cp SourceHanSerifSC-Regular.otf "$FONT_DIR/"
        echo "✅ 思源宋体安装完成"
    fi
else
    echo "✅ 思源宋体已安装"
fi

# 思源黑体
if [ ! -f "$FONT_DIR/SourceHanSansSC-Regular.otf" ]; then
    echo "下载思源黑体..."
    cd /tmp
    wget -q https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf -O SourceHanSansSC-Regular.otf 2>/dev/null || {
        echo "⚠️  无法从GitHub下载思源黑体，请手动下载并安装"
        echo "   下载地址: https://github.com/adobe-fonts/source-han-sans/releases"
    }
    if [ -f "SourceHanSansSC-Regular.otf" ]; then
        sudo cp SourceHanSansSC-Regular.otf "$FONT_DIR/"
        echo "✅ 思源黑体安装完成"
    fi
else
    echo "✅ 思源黑体已安装"
fi

# 2. 安装文泉驿字体（已有，但确保完整）
echo ""
echo "2. 检查文泉驿字体..."
echo "----------------------------------------"
if fc-list | grep -i "WenQuanYi" > /dev/null; then
    echo "✅ 文泉驿字体已安装"
else
    echo "⚠️  文泉驿字体未找到"
fi

# 3. 安装楷体（使用文泉驿楷体或思源字体）
echo ""
echo "3. 检查楷体..."
echo "----------------------------------------"
# 文泉驿楷体
if [ ! -f "$FONT_DIR/wqy-zenhei.ttc" ]; then
    echo "下载文泉驿正黑（可用作楷体替代）..."
    # 文泉驿正黑通常已包含在系统中，如果没有，可以安装
    echo "⚠️  如果缺少楷体，可以使用文泉驿正黑替代"
else
    echo "✅ 文泉驿正黑已安装"
fi

# 4. 安装Times New Roman替代字体（Liberation Serif）
echo ""
echo "4. 检查Times New Roman替代字体..."
echo "----------------------------------------"
if fc-list | grep -i "Liberation Serif" > /dev/null; then
    echo "✅ Liberation Serif已安装（Times New Roman替代）"
else
    echo "⚠️  Liberation Serif未找到"
fi

# 5. 更新字体缓存
echo ""
echo "5. 更新字体缓存..."
echo "----------------------------------------"
sudo fc-cache -fv
echo ""

# 6. 验证安装
echo "6. 验证字体安装..."
echo "----------------------------------------"
echo "中文字体列表："
fc-list :lang=zh | head -n 10
echo ""
echo "总字体数: $(fc-list | wc -l)"
echo "中文字体数: $(fc-list :lang=zh | wc -l)"
echo ""

echo "=========================================="
echo "字体安装完成"
echo "=========================================="
echo ""
echo "注意："
echo "1. 如果GitHub下载失败，请手动下载字体文件到 $FONT_DIR/"
echo "2. 思源字体下载地址："
echo "   - 思源宋体: https://github.com/adobe-fonts/source-han-serif/releases"
echo "   - 思源黑体: https://github.com/adobe-fonts/source-han-sans/releases"
echo "3. 安装后需要重启LibreOffice或重启服务才能生效"
echo ""

