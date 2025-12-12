#!/bin/bash

echo "=========================================="
echo "诊断502连接问题"
echo "=========================================="
echo ""

echo "1. 测试本地8000端口连接..."
echo "----------------------------------------"
curl -v http://127.0.0.1:8000/docs 2>&1 | head -n 30
echo ""

echo "2. 检查Gunicorn是否在监听8000端口..."
echo "----------------------------------------"
sudo netstat -tlnp 2>/dev/null | grep 8000 || sudo ss -tlnp 2>/dev/null | grep 8000
echo ""

echo "3. 检查Nginx配置..."
echo "----------------------------------------"
sudo nginx -t 2>&1
echo ""

echo "4. 检查Nginx错误日志（最近的502错误）..."
echo "----------------------------------------"
sudo tail -n 30 /var/log/nginx/error.log | grep -i "502\|upstream\|connect" | tail -n 10
echo ""

echo "5. 检查应用程序错误日志（最近的错误）..."
echo "----------------------------------------"
sudo tail -n 50 /var/log/geshixiugai/error.log | grep -i "error\|exception\|traceback\|failed" | tail -n 15
echo ""

echo "6. 检查是否有worker进程崩溃..."
echo "----------------------------------------"
ps aux | grep gunicorn | grep -v grep | wc -l
echo "当前Gunicorn进程数（应该等于workers+1）"
echo ""

echo "7. 测试简单的API端点..."
echo "----------------------------------------"
curl -s http://127.0.0.1:8000/ 2>&1 | head -n 5 || echo "连接失败"
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果本地8000端口无法连接，可能是："
echo "1. 服务在处理请求时崩溃"
echo "2. 服务响应超时"
echo "3. 端口被其他进程占用"
echo ""
echo "建议："
echo "1. 查看完整错误日志: sudo tail -n 100 /var/log/geshixiugai/error.log"
echo "2. 重启服务: sudo systemctl restart geshixiugai"
echo "3. 检查Nginx日志: sudo tail -n 50 /var/log/nginx/error.log"

