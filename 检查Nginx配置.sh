#!/bin/bash

# 检查Nginx配置和连接

echo "=========================================="
echo "检查Nginx配置和连接"
echo "=========================================="
echo ""

# 1. 检查Nginx状态
echo "1. Nginx状态..."
echo "----------------------------------------"
sudo systemctl status nginx --no-pager | head -n 15
echo ""

# 2. 检查端口监听
echo "2. 端口监听情况..."
echo "----------------------------------------"
echo "8000端口（后端）:"
sudo netstat -tlnp | grep 8000 || ss -tlnp | grep 8000
echo ""
echo "80端口（Nginx）:"
sudo netstat -tlnp | grep :80 || ss -tlnp | grep :80
echo ""

# 3. 测试后端服务连接
echo "3. 测试后端服务连接..."
echo "----------------------------------------"
echo "测试 http://127.0.0.1:8000/docs"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://127.0.0.1:8000/docs || echo "连接失败"
echo ""

# 4. 检查Nginx配置
echo "4. 检查Nginx配置..."
echo "----------------------------------------"
if [ -f /etc/nginx/conf.d/geshixiugai.conf ]; then
    echo "配置文件: /etc/nginx/conf.d/geshixiugai.conf"
    cat /etc/nginx/conf.d/geshixiugai.conf | grep -E "proxy_pass|upstream|server_name" | head -n 10
elif [ -f /etc/nginx/sites-available/geshixiugai ]; then
    echo "配置文件: /etc/nginx/sites-available/geshixiugai"
    cat /etc/nginx/sites-available/geshixiugai | grep -E "proxy_pass|upstream|server_name" | head -n 10
else
    echo "查找Nginx配置文件..."
    sudo find /etc/nginx -name "*geshixiugai*" -o -name "*default*" 2>/dev/null | head -n 5
fi
echo ""

# 5. 检查Nginx错误日志
echo "5. 最近的Nginx错误日志..."
echo "----------------------------------------"
sudo tail -n 30 /var/log/nginx/error.log 2>/dev/null | grep -E "502|upstream|connect" | tail -n 10
echo ""

# 6. 测试Nginx到后端的连接
echo "6. 测试Nginx到后端的连接..."
echo "----------------------------------------"
echo "从服务器内部测试后端API..."
curl -s http://127.0.0.1:8000/api/health 2>&1 | head -n 5 || echo "健康检查端点不存在，尝试其他端点..."
curl -s http://127.0.0.1:8000/docs 2>&1 | head -n 5 || echo "无法连接到后端"
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果后端服务正常但Nginx无法连接，可能需要："
echo "1. 检查Nginx配置中的proxy_pass地址"
echo "2. 检查防火墙设置"
echo "3. 重启Nginx: sudo systemctl restart nginx"
echo ""



