#!/bin/bash

# 快速部署脚本 - geshixiugai.cn
# 服务器 IP: 121.199.49.1
# 使用方法：在服务器上运行此脚本

set -e

echo "🚀 开始部署 geshixiugai.cn 到阿里云服务器..."
echo "📋 服务器 IP: 121.199.49.1"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 用户运行此脚本"
    exit 1
fi

# 项目目录
PROJECT_DIR="/var/www/geshixiugai"

echo "📋 步骤 1: 创建项目目录"
mkdir -p /var/www
cd /var/www

echo "📋 步骤 2: 克隆代码"
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  项目目录已存在，跳过克隆"
    cd $PROJECT_DIR
    git pull || echo "⚠️  Git pull 失败，请手动检查"
else
    git clone https://github.com/jet20002025-hash/geshixiugai.git geshixiugai
    cd geshixiugai
fi

echo "📋 步骤 3: 运行部署脚本"
chmod +x deploy_aliyun.sh
./deploy_aliyun.sh

echo ""
echo "✅ 部署脚本执行完成！"
echo ""
echo "📋 下一步操作："
echo "1. 配置环境变量："
echo "   cd $PROJECT_DIR"
echo "   cp env.example .env"
echo "   nano .env"
echo ""
echo "2. 重启服务："
echo "   sudo systemctl restart geshixiugai"
echo ""
echo "3. 配置域名解析（阿里云 DNS 控制台）："
echo "   - 主机记录: @, 记录值: 121.199.49.1"
echo "   - 主机记录: www, 记录值: 121.199.49.1"
echo ""
echo "4. 配置 SSL 证书："
echo "   sudo apt install -y certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d geshixiugai.cn -d www.geshixiugai.cn"
echo ""










