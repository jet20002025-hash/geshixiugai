#!/bin/bash
# 安装宋体字体脚本

echo "=== 安装宋体字体 ==="

# 创建字体目录
sudo mkdir -p /usr/share/fonts/chinese

# 下载宋体字体（SimSun）
cd /tmp
echo "下载宋体字体..."

# 方法1: 从GitHub下载（如果可用）
if [ ! -f "simsun.ttf" ]; then
    # 尝试下载宋体字体
    # 注意：由于版权问题，可能需要从其他来源获取
    # 这里提供一个通用的下载方法
    
    # 尝试从公共字体库下载
    curl -L -o simsun.ttf \
      "https://github.com/adobe-fonts/source-han-serif/raw/release/OTF/SimplifiedChinese/SourceHanSerifSC-Regular.otf" 2>/dev/null || \
    echo "提示：如果下载失败，请手动上传 simsun.ttf 到 /tmp/ 目录"
fi

# 如果下载成功，安装字体
if [ -f "simsun.ttf" ]; then
    echo "✅ 字体文件下载成功"
    sudo cp simsun.ttf /usr/share/fonts/chinese/
    sudo chmod 644 /usr/share/fonts/chinese/simsun.ttf
    echo "✅ 字体文件已复制到系统字体目录"
else
    echo "⚠️ 如果 simsun.ttf 已存在于 /tmp/ 目录，将使用该文件"
    if [ -f "/tmp/simsun.ttf" ]; then
        sudo cp /tmp/simsun.ttf /usr/share/fonts/chinese/
        sudo chmod 644 /usr/share/fonts/chinese/simsun.ttf
        echo "✅ 使用本地字体文件"
    else
        echo "❌ 未找到字体文件，请手动下载并放置到 /tmp/simsun.ttf"
        echo "提示：可以从 Windows 系统复制 simsun.ttf 文件"
    fi
fi

# 更新字体缓存
echo "更新字体缓存..."
sudo fc-cache -fv

# 验证安装
echo -e "\n=== 验证字体安装 ==="
if fc-list :lang=zh | grep -i "song\|simsun\|simsun" > /dev/null; then
    echo "✅ 宋体字体安装成功！"
    fc-list :lang=zh | grep -i "song\|simsun"
else
    echo "⚠️ 未检测到宋体字体，但可能已安装其他中文字体"
    echo "已安装的中文字体："
    fc-list :lang=zh | head -5
fi

echo -e "\n=== 完成 ==="




