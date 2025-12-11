#!/bin/bash

# 检查服务是否正常运行

echo "=========================================="
echo "检查服务是否正常运行"
echo "=========================================="
echo ""

# 1. 等待几秒让服务完全启动
echo "1. 等待服务完全启动（5秒）..."
sleep 5
echo ""

# 2. 再次检查服务状态
echo "2. 检查服务状态..."
sudo systemctl status geshixiugai --no-pager | head -n 20
echo ""

# 3. 检查端口8000是否被监听
echo "3. 检查端口8000监听情况..."
sudo netstat -tlnp | grep 8000 || ss -tlnp | grep 8000
echo ""

# 4. 测试本地连接
echo "4. 测试本地连接..."
echo "测试 /docs 端点:"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://127.0.0.1:8000/docs
echo ""

echo "测试根路径:"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://127.0.0.1:8000/
echo ""

# 5. 检查最近的日志
echo "5. 检查最近的日志（最后20行）..."
sudo journalctl -u geshixiugai -n 20 --no-pager | tail -n 20
echo ""

# 6. 检查Nginx状态
echo "6. 检查Nginx状态..."
sudo systemctl status nginx --no-pager | head -n 10
echo ""

# 7. 检查Nginx错误日志
echo "7. 检查Nginx错误日志（最后10行）..."
sudo tail -n 10 /var/log/nginx/geshixiugai_error.log 2>/dev/null || sudo tail -n 10 /var/log/nginx/error.log 2>/dev/null | grep -E "502|upstream|connect" || echo "无相关错误"
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果本地连接返回200，但网页仍显示502，可能是："
echo "1. Nginx配置问题"
echo "2. Nginx需要重启"
echo "3. 防火墙问题"
echo ""
echo "可以尝试重启Nginx:"
echo "  sudo systemctl restart nginx"
echo ""

