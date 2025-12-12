#!/bin/bash

# 深度诊断502错误

echo "=========================================="
echo "深度诊断502错误"
echo "=========================================="
echo ""

# 1. 检查后端服务是否真的在监听8000端口
echo "1. 检查8000端口监听情况..."
echo "----------------------------------------"
sudo netstat -tlnp | grep 8000
sudo ss -tlnp | grep 8000
echo ""

# 2. 测试后端服务
echo "2. 测试后端服务响应..."
echo "----------------------------------------"
echo "测试 /docs 端点:"
curl -v http://127.0.0.1:8000/docs 2>&1 | grep -E "HTTP|Connected|Connection" | head -n 5
echo ""
echo "测试 /api/health 端点（如果存在）:"
curl -s http://127.0.0.1:8000/api/health 2>&1 | head -n 3 || echo "健康检查端点不存在"
echo ""

# 3. 检查后端服务进程
echo "3. 检查后端服务进程..."
echo "----------------------------------------"
ps aux | grep -E "gunicorn|uvicorn" | grep -v grep
echo ""

# 4. 检查最近的错误日志
echo "4. 检查最近的错误日志..."
echo "----------------------------------------"
echo "Gunicorn日志:"
sudo journalctl -u geshixiugai -n 50 --no-pager | grep -E "ERROR|error|Exception|Traceback|502" | tail -n 20
echo ""
echo "错误日志文件:"
tail -n 30 /var/log/geshixiugai/error.log 2>/dev/null | grep -E "ERROR|error|Exception|Traceback" | tail -n 15 || echo "无法读取错误日志文件"
echo ""

# 5. 检查Nginx错误日志
echo "5. 检查Nginx错误日志..."
echo "----------------------------------------"
sudo tail -n 30 /var/log/nginx/geshixiugai_error.log 2>/dev/null | tail -n 15 || sudo tail -n 30 /var/log/nginx/error.log | grep -E "502|upstream|connect" | tail -n 15
echo ""

# 6. 测试从Nginx到后端的连接
echo "6. 测试从Nginx到后端的连接..."
echo "----------------------------------------"
echo "模拟Nginx请求:"
curl -H "Host: www.geshixiugai.cn" http://127.0.0.1:8000/docs 2>&1 | head -n 5
echo ""

# 7. 检查服务资源使用
echo "7. 检查服务资源使用..."
echo "----------------------------------------"
systemctl show geshixiugai | grep -E "MemoryCurrent|TasksCurrent" || echo "无法获取资源信息"
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果后端服务未监听8000端口，请重启服务："
echo "  sudo systemctl restart geshixiugai"
echo ""
echo "如果后端服务响应正常但Nginx仍然502，请重启Nginx："
echo "  sudo systemctl restart nginx"
echo ""



