#!/bin/bash

# 在服务器上直接下载字体文件
# 如果无法从本地上传，可以使用此脚本

echo "=========================================="
echo "在服务器上直接下载字体文件"
echo "=========================================="
echo ""

FONT_DIR="/usr/share/fonts/chinese"
sudo mkdir -p "$FONT_DIR"
cd /tmp

echo "注意：此脚本需要字体文件的下载链接"
echo "如果字体文件在网盘或其他位置，请提供下载链接"
echo ""

# 方法1：如果有字体文件的下载链接
echo "方法1：从下载链接获取字体"
echo "----------------------------------------"
echo "如果您有字体文件的下载链接，可以使用wget下载："
echo ""
echo "例如："
echo "  wget -O simsun.ttc 'https://example.com/simsun.ttc'"
echo "  wget -O simhei.ttf 'https://example.com/simhei.ttf'"
echo "  wget -O kaiu.ttf 'https://example.com/kaiu.ttf'"
echo "  wget -O times.ttf 'https://example.com/times.ttf'"
echo ""

# 方法2：从Windows系统复制（如果服务器可以访问Windows共享）
echo "方法2：从Windows共享获取"
echo "----------------------------------------"
echo "如果服务器可以访问Windows共享，可以使用："
echo ""
echo "  # 安装cifs-utils"
echo "  sudo yum install -y cifs-utils"
echo ""
echo "  # 挂载Windows共享"
echo "  sudo mount -t cifs //windows-ip/shared /mnt/windows -o username=user,password=pass"
echo ""
echo "  # 复制字体文件"
echo "  sudo cp /mnt/windows/Windows/Fonts/simsun.ttc /tmp/"
echo ""

# 方法3：使用base64编码传输（如果文件较小）
echo "方法3：使用base64编码传输"
echo "----------------------------------------"
echo "如果文件较小，可以在本地编码后粘贴到服务器："
echo ""
echo "在本地Mac上："
echo "  base64 SIMSUN.TTC | pbcopy"
echo ""
echo "然后在服务器上："
echo "  # 粘贴base64内容到文件"
echo "  nano /tmp/simsun_base64.txt"
echo "  # 粘贴内容，保存退出"
echo ""
echo "  # 解码"
echo "  base64 -d /tmp/simsun_base64.txt > /tmp/simsun.ttc"
echo ""

echo "=========================================="
echo "推荐方案"
echo "=========================================="
echo ""
echo "1. 使用FileZilla等SFTP客户端（最简单）"
echo "2. 配置SSH密钥登录（最安全）"
echo "3. 在服务器上直接下载（如果有下载链接）"
echo ""



