#!/bin/bash

# 详细诊断502错误

echo "=========================================="
echo "详细诊断502 Bad Gateway错误"
echo "=========================================="
echo ""

# 1. 等待服务完全启动
echo "1. 等待服务完全启动（10秒）..."
sleep 10
echo ""

# 2. 检查服务状态
echo "2. 检查服务状态..."
sudo systemctl status geshixiugai --no-pager | head -n 25
echo ""

# 3. 检查进程
echo "3. 检查Gunicorn进程..."
ps aux | grep gunicorn | grep -v grep
echo ""

# 4. 检查端口监听
echo "4. 检查端口8000监听..."
echo "使用 netstat:"
sudo netstat -tlnp | grep 8000 || echo "未找到8000端口监听"
echo ""
echo "使用 ss:"
sudo ss -tlnp | grep 8000 || echo "未找到8000端口监听"
echo ""

# 5. 测试本地连接
echo "5. 测试本地连接..."
echo "测试 /docs 端点:"
curl -v http://127.0.0.1:8000/docs 2>&1 | head -n 15
echo ""

echo "测试根路径:"
curl -v http://127.0.0.1:8000/ 2>&1 | head -n 15
echo ""

# 6. 检查应用日志
echo "6. 检查应用启动日志（最后50行）..."
sudo journalctl -u geshixiugai -n 50 --no-pager | tail -n 50
echo ""

# 7. 检查是否有错误
echo "7. 检查错误日志..."
sudo journalctl -u geshixiugai -n 100 --no-pager | grep -iE "error|exception|traceback|failed|502" | tail -n 20
echo ""

# 8. 检查Nginx状态
echo "8. 检查Nginx状态..."
sudo systemctl status nginx --no-pager | head -n 15
echo ""

# 9. 检查Nginx错误日志
echo "9. 检查Nginx错误日志..."
if [ -f "/var/log/nginx/geshixiugai_error.log" ]; then
    echo "geshixiugai_error.log (最后20行):"
    sudo tail -n 20 /var/log/nginx/geshixiugai_error.log
else
    echo "从 error.log 查找相关错误:"
    sudo tail -n 50 /var/log/nginx/error.log | grep -E "502|upstream|connect|geshixiugai" | tail -n 20
fi
echo ""

# 10. 检查Nginx配置
echo "10. 检查Nginx配置..."
sudo nginx -t
echo ""

# 11. 测试从Nginx到后端的连接
echo "11. 测试从Nginx到后端的连接..."
curl -H "Host: geshixiugai.cn" http://127.0.0.1/docs 2>&1 | head -n 10
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果本地连接（127.0.0.1:8000）正常，但网页仍显示502，请："
echo "1. 重启Nginx: sudo systemctl restart nginx"
echo "2. 检查Nginx配置中的 proxy_pass 是否正确指向 http://127.0.0.1:8000"
echo ""
echo "如果本地连接失败，请查看上面的错误日志"
echo ""


