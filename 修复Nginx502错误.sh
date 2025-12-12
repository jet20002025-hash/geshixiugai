#!/bin/bash

# 修复Nginx 502错误

echo "=========================================="
echo "修复Nginx 502错误"
echo "=========================================="
echo ""

# 1. 查找Nginx配置文件
echo "1. 查找Nginx配置文件..."
echo "----------------------------------------"
NGINX_CONF=""
if [ -f /etc/nginx/conf.d/geshixiugai.conf ]; then
    NGINX_CONF="/etc/nginx/conf.d/geshixiugai.conf"
elif [ -f /etc/nginx/sites-available/geshixiugai ]; then
    NGINX_CONF="/etc/nginx/sites-available/geshixiugai"
elif [ -f /etc/nginx/nginx.conf ]; then
    NGINX_CONF="/etc/nginx/nginx.conf"
fi

if [ -z "$NGINX_CONF" ]; then
    echo "查找所有可能的配置文件..."
    sudo find /etc/nginx -name "*.conf" -type f 2>/dev/null | head -n 5
    echo ""
    echo "请手动指定配置文件路径"
    exit 1
fi

echo "找到配置文件: $NGINX_CONF"
echo ""

# 2. 检查配置
echo "2. 检查当前配置..."
echo "----------------------------------------"
sudo grep -A 10 "proxy_pass" "$NGINX_CONF" | head -n 15
echo ""

# 3. 检查后端服务连接
echo "3. 测试后端服务连接..."
echo "----------------------------------------"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://127.0.0.1:8000/docs
echo ""

# 4. 检查Nginx错误日志
echo "4. 最近的Nginx错误..."
echo "----------------------------------------"
sudo tail -n 20 /var/log/nginx/error.log | grep -E "502|upstream|connect|timeout" | tail -n 10
echo ""

# 5. 建议修复
echo "=========================================="
echo "建议的修复步骤"
echo "=========================================="
echo ""
echo "1. 确保Nginx配置中的proxy_pass指向正确的地址："
echo "   proxy_pass http://127.0.0.1:8000;"
echo ""
echo "2. 增加超时时间（如果请求处理时间较长）："
echo "   proxy_read_timeout 300s;"
echo "   proxy_connect_timeout 60s;"
echo "   proxy_send_timeout 300s;"
echo ""
echo "3. 重启Nginx："
echo "   sudo systemctl restart nginx"
echo ""
echo "4. 如果问题仍然存在，检查Nginx配置语法："
echo "   sudo nginx -t"
echo ""



