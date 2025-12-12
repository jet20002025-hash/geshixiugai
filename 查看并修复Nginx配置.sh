#!/bin/bash

# 查看并修复Nginx配置

echo "=========================================="
echo "查看并修复Nginx配置"
echo "=========================================="
echo ""

NGINX_CONF="/etc/nginx/conf.d/geshixiugai.conf"

# 1. 查看当前配置
echo "1. 当前Nginx配置..."
echo "----------------------------------------"
sudo cat "$NGINX_CONF"
echo ""

# 2. 检查关键配置项
echo "2. 检查关键配置项..."
echo "----------------------------------------"
echo "proxy_pass配置:"
sudo grep -A 5 "proxy_pass" "$NGINX_CONF" | head -n 10
echo ""
echo "超时设置:"
sudo grep -E "timeout|proxy_read|proxy_connect|proxy_send" "$NGINX_CONF" || echo "未找到超时设置"
echo ""

# 3. 测试配置语法
echo "3. 测试Nginx配置语法..."
echo "----------------------------------------"
sudo nginx -t
echo ""

# 4. 检查后端服务
echo "4. 检查后端服务..."
echo "----------------------------------------"
curl -s -o /dev/null -w "后端服务状态码: %{http_code}\n" http://127.0.0.1:8000/docs
echo ""

# 5. 建议修复
echo "=========================================="
echo "建议的配置修复"
echo "=========================================="
echo ""
echo "如果配置中缺少超时设置，建议添加以下内容到location块中："
echo ""
echo "  proxy_read_timeout 300s;"
echo "  proxy_connect_timeout 60s;"
echo "  proxy_send_timeout 300s;"
echo "  proxy_buffering off;"
echo ""
echo "完整的location块示例："
echo "  location / {"
echo "      proxy_pass http://127.0.0.1:8000;"
echo "      proxy_set_header Host \$host;"
echo "      proxy_set_header X-Real-IP \$remote_addr;"
echo "      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "      proxy_set_header X-Forwarded-Proto \$scheme;"
echo "      proxy_read_timeout 300s;"
echo "      proxy_connect_timeout 60s;"
echo "      proxy_send_timeout 300s;"
echo "      proxy_buffering off;"
echo "  }"
echo ""



