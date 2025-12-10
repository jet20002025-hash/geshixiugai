#!/bin/bash
# 快速安装中文字体脚本（适用于 CentOS/RHEL/Alibaba Cloud Linux）

echo "=== 检查系统信息 ==="
cat /etc/os-release | grep -E "NAME|VERSION"

echo -e "\n=== 方法1: 尝试从 EPEL 安装 ==="
# 检查是否已安装 EPEL
if ! rpm -qa | grep -q epel-release; then
    echo "安装 EPEL 仓库..."
    sudo yum install -y epel-release
fi

# 尝试安装文泉驿字体
echo "尝试安装文泉驿字体..."
sudo yum install -y wqy-microhei-fonts 2>/dev/null && echo "✅ 安装成功" || echo "❌ 安装失败，尝试方法2"

echo -e "\n=== 方法2: 手动下载安装字体 ==="
# 创建字体目录
sudo mkdir -p /usr/share/fonts/chinese

# 下载文泉驿微米黑字体（从 GitHub）
cd /tmp
if [ ! -f "wqy-microhei.ttc" ]; then
    echo "下载字体文件..."
    # 使用多个镜像源尝试下载
    wget -q --timeout=10 https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc 2>/dev/null || \
    wget -q --timeout=10 https://raw.githubusercontent.com/anthonyfok/fonts-wqy-microhei/master/wqy-microhei.ttc 2>/dev/null || \
    curl -L -o wqy-microhei.ttc https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc 2>/dev/null
    
    if [ -f "wqy-microhei.ttc" ]; then
        echo "✅ 字体文件下载成功"
        sudo cp wqy-microhei.ttc /usr/share/fonts/chinese/
        sudo chmod 644 /usr/share/fonts/chinese/wqy-microhei.ttc
    else
        echo "❌ 字体文件下载失败，尝试方法3"
    fi
fi

echo -e "\n=== 方法3: 使用系统已有字体 ==="
# 检查系统中是否已有中文字体
EXISTING_FONT=$(find /usr/share/fonts -name "*song*" -o -name "*hei*" -o -name "*sim*" 2>/dev/null | head -1)
if [ -n "$EXISTING_FONT" ]; then
    echo "✅ 找到已有字体: $EXISTING_FONT"
    # 创建符号链接到 chinese 目录
    sudo mkdir -p /usr/share/fonts/chinese
    sudo ln -sf "$EXISTING_FONT" /usr/share/fonts/chinese/ 2>/dev/null || true
fi

echo -e "\n=== 更新字体缓存 ==="
sudo fc-cache -fv

echo -e "\n=== 验证字体安装 ==="
if fc-list :lang=zh 2>/dev/null | grep -q .; then
    echo "✅ 中文字体安装成功！"
    echo "已安装的中文字体："
    fc-list :lang=zh | head -5
else
    echo "❌ 未找到中文字体，请手动安装"
    echo "提示：可以手动下载字体文件到 /usr/share/fonts/chinese/ 目录"
fi

echo -e "\n=== 完成 ==="


