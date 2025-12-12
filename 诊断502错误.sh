#!/bin/bash

# 诊断502 Bad Gateway错误

echo "=========================================="
echo "诊断502 Bad Gateway错误"
echo "=========================================="
echo ""

# 1. 检查后端服务状态
echo "1. 检查后端服务状态..."
echo "----------------------------------------"
sudo systemctl status geshixiugai --no-pager | head -n 20
echo ""

# 2. 检查服务是否在运行
echo "2. 检查服务进程..."
echo "----------------------------------------"
ps aux | grep -E "gunicorn|geshixiugai" | grep -v grep
echo ""

# 3. 检查端口8000是否被监听
echo "3. 检查端口8000..."
echo "----------------------------------------"
sudo netstat -tlnp | grep 8000 || ss -tlnp | grep 8000
echo ""

# 4. 检查Nginx状态
echo "4. 检查Nginx状态..."
echo "----------------------------------------"
sudo systemctl status nginx --no-pager | head -n 15
echo ""

# 5. 检查最近的错误日志
echo "5. 检查最近的错误日志..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 50 --no-pager | tail -n 30
echo ""

# 6. 检查Nginx错误日志
echo "6. 检查Nginx错误日志..."
echo "----------------------------------------"
sudo tail -n 20 /var/log/nginx/error.log 2>/dev/null || echo "无法读取Nginx错误日志"
echo ""

# 7. 测试后端服务连接
echo "7. 测试后端服务连接..."
echo "----------------------------------------"
curl -v http://127.0.0.1:8000/docs 2>&1 | head -n 10 || echo "无法连接到后端服务"
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果服务未运行，请执行："
echo "  sudo systemctl restart geshixiugai"
echo ""
echo "如果服务启动失败，请检查日志："
echo "  sudo journalctl -u geshixiugai -n 100 --no-pager"
echo ""



