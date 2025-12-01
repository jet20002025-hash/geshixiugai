#!/bin/bash

# 阿里云服务器部署脚本
# 使用方法：在服务器上运行此脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署到阿里云服务器..."

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ 请使用 root 用户运行此脚本${NC}"
    exit 1
fi

# 项目目录
PROJECT_DIR="/var/www/geshixiugai"
LOG_DIR="/var/log/geshixiugai"

echo -e "${GREEN}📋 步骤 1: 更新系统包${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}📋 步骤 2: 安装基础工具${NC}"
apt install -y git curl wget vim software-properties-common build-essential libssl-dev libffi-dev

echo -e "${GREEN}📋 步骤 3: 安装 Python 3.12${NC}"
if ! command -v python3.12 &> /dev/null; then
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update
    apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
else
    echo "Python 3.12 已安装"
fi

echo -e "${GREEN}📋 步骤 4: 安装 Nginx${NC}"
if ! command -v nginx &> /dev/null; then
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
else
    echo "Nginx 已安装"
fi

echo -e "${GREEN}📋 步骤 5: 创建项目目录${NC}"
mkdir -p $PROJECT_DIR
mkdir -p $LOG_DIR
chown -R www-data:www-data $LOG_DIR

echo -e "${GREEN}📋 步骤 6: 检查代码是否已克隆${NC}"
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo -e "${YELLOW}⚠️  代码目录不存在，请先克隆代码：${NC}"
    echo "   cd /var/www"
    echo "   git clone https://github.com/jet20002025-hash/geshixiugai.git geshixiugai"
    echo ""
    read -p "代码是否已克隆到 $PROJECT_DIR? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ 请先克隆代码后再运行此脚本${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}📋 步骤 7: 创建虚拟环境${NC}"
cd $PROJECT_DIR
if [ ! -d "venv" ]; then
    python3.12 -m venv venv
    echo "虚拟环境已创建"
else
    echo "虚拟环境已存在"
fi

echo -e "${GREEN}📋 步骤 8: 安装 Python 依赖${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}📋 步骤 9: 检查 .env 文件${NC}"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，正在创建模板...${NC}"
    cat > $PROJECT_DIR/.env << 'EOF'
# 存储配置（选择一种）
# Supabase Storage
SUPABASE_URL=https://你的项目ID.supabase.co
SUPABASE_KEY=你的service_role key
SUPABASE_BUCKET=word-formatter-storage

# 或 Cloudflare R2
# R2_ACCOUNT_ID=你的Account ID
# R2_ACCESS_KEY_ID=你的Access Key ID
# R2_SECRET_ACCESS_KEY=你的Secret Access Key
# R2_BUCKET_NAME=word-formatter-storage
# R2_ENDPOINT=https://你的Account ID.r2.cloudflarestorage.com

# 支付配置（可选）
# ALIPAY_APP_ID=你的支付宝AppID
# ALIPAY_PRIVATE_KEY=你的支付宝私钥
# ALIPAY_PUBLIC_KEY=支付宝公钥
EOF
    chown www-data:www-data $PROJECT_DIR/.env
    chmod 600 $PROJECT_DIR/.env
    echo -e "${YELLOW}⚠️  请编辑 .env 文件并填入正确的配置信息${NC}"
    echo "   文件位置: $PROJECT_DIR/.env"
    read -p "按 Enter 继续（请确保已配置 .env 文件）..."
else
    echo ".env 文件已存在"
fi

echo -e "${GREEN}📋 步骤 10: 配置 Nginx${NC}"
if [ ! -f "/etc/nginx/sites-available/geshixiugai" ]; then
    cat > /etc/nginx/sites-available/geshixiugai << 'EOF'
server {
    listen 80;
    server_name geshixiugai.cn www.geshixiugai.cn;

    # 设置请求体大小限制（50MB）
    client_max_body_size 50m;

    # 增加超时时间（用于大文件上传）
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    # 日志
    access_log /var/log/nginx/geshixiugai_access.log;
    error_log /var/log/nginx/geshixiugai_error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    echo "Nginx 配置文件已创建"
else
    echo "Nginx 配置文件已存在"
fi

# 启用站点
if [ ! -L "/etc/nginx/sites-enabled/geshixiugai" ]; then
    ln -s /etc/nginx/sites-available/geshixiugai /etc/nginx/sites-enabled/
    echo "Nginx 站点已启用"
fi

# 测试 Nginx 配置
nginx -t
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo "Nginx 配置已重新加载"
else
    echo -e "${RED}❌ Nginx 配置有误，请检查${NC}"
    exit 1
fi

echo -e "${GREEN}📋 步骤 11: 配置 Systemd 服务${NC}"
if [ ! -f "/etc/systemd/system/geshixiugai.service" ]; then
    cat > /etc/systemd/system/geshixiugai.service << EOF
[Unit]
Description=Geshixiugai API Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -c gunicorn_config.py backend.app.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    echo "Systemd 服务文件已创建"
else
    echo "Systemd 服务文件已存在"
fi

# 重新加载 systemd
systemctl daemon-reload

echo -e "${GREEN}📋 步骤 12: 启动服务${NC}"
systemctl enable geshixiugai
systemctl restart geshixiugai

# 等待服务启动
sleep 2

# 检查服务状态
if systemctl is-active --quiet geshixiugai; then
    echo -e "${GREEN}✅ 服务已启动${NC}"
else
    echo -e "${RED}❌ 服务启动失败，请检查日志：${NC}"
    echo "   sudo journalctl -u geshixiugai -n 50"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo "📋 下一步操作："
echo "1. 配置域名解析："
echo "   - 在阿里云 DNS 控制台添加 A 记录"
echo "   - 主机记录: @ 和 www"
echo "   - 记录值: 你的服务器公网 IP"
echo ""
echo "2. 配置 SSL 证书："
echo "   sudo apt install -y certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d geshixiugai.cn -d www.geshixiugai.cn"
echo ""
echo "3. 查看服务状态："
echo "   sudo systemctl status geshixiugai"
echo ""
echo "4. 查看日志："
echo "   sudo journalctl -u geshixiugai -f"
echo "   sudo tail -f /var/log/nginx/geshixiugai_error.log"
echo ""
echo "5. 测试访问："
echo "   curl http://localhost:8000"
echo "   curl http://你的公网IP"
echo ""


