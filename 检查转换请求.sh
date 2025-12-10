#!/bin/bash

# 检查转换请求的脚本

echo "=========================================="
echo "检查转换请求"
echo "=========================================="
echo ""

# 1. 查看所有最近的日志（不筛选）
echo "1. 查看所有最近的日志（最后 50 行，不筛选）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 50 --no-pager | tail -n 30
echo "----------------------------------------"
echo ""

# 2. 查看访问日志
echo "2. 查看访问日志..."
if [ -f "/var/log/geshixiugai/access.log" ]; then
    echo "✅ 访问日志文件存在"
    echo "最近的访问记录（最后 20 行）："
    sudo tail -n 20 /var/log/geshixiugai/access.log
else
    echo "⚠️ 访问日志文件不存在: /var/log/geshixiugai/access.log"
fi
echo ""

# 3. 查看错误日志
echo "3. 查看错误日志..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    ERROR_COUNT=$(sudo tail -n 100 /var/log/geshixiugai/error.log | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "最近的错误日志（最后 30 行）："
        sudo tail -n 30 /var/log/geshixiugai/error.log
    else
        echo "⚠️ 错误日志文件为空"
    fi
else
    echo "⚠️ 错误日志文件不存在"
fi
echo ""

# 4. 查看 Nginx 访问日志（如果有）
echo "4. 查看 Nginx 访问日志..."
if [ -f "/var/log/nginx/geshixiugai_access.log" ]; then
    echo "✅ Nginx 访问日志存在"
    echo "最近的访问记录（最后 20 行）："
    sudo tail -n 20 /var/log/nginx/geshixiugai_access.log | grep -E "convert|POST|GET" | tail -n 10
else
    echo "⚠️ Nginx 访问日志不存在"
    echo "   检查其他 Nginx 日志文件..."
    ls -la /var/log/nginx/*.log 2>/dev/null | head -n 5
fi
echo ""

# 5. 查看 Nginx 错误日志
echo "5. 查看 Nginx 错误日志..."
if [ -f "/var/log/nginx/geshixiugai_error.log" ]; then
    echo "✅ Nginx 错误日志存在"
    ERROR_COUNT=$(sudo tail -n 50 /var/log/nginx/geshixiugai_error.log | grep -v "^$" | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "最近的错误（最后 20 行）："
        sudo tail -n 20 /var/log/nginx/geshixiugai_error.log
    else
        echo "✅ 没有错误"
    fi
else
    echo "⚠️ Nginx 错误日志不存在"
fi
echo ""

# 6. 检查是否有 POST 请求到 /documents/convert-to-pdf
echo "6. 检查转换请求..."
echo "在应用日志中搜索 convert-to-pdf..."
sudo journalctl -u geshixiugai -n 500 --no-pager | grep -iE "convert|POST|/documents" | tail -n 20
echo ""

# 7. 检查进程是否在处理请求
echo "7. 检查 Gunicorn 进程..."
ps aux | grep gunicorn | grep -v grep
echo ""

# 8. 测试 API 端点（模拟请求）
echo "8. 测试转换 API 端点..."
echo "执行: curl -X POST http://localhost:8000/documents/convert-to-pdf"
curl -X POST http://localhost:8000/documents/convert-to-pdf 2>&1 | head -n 10
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果日志中没有转换相关的记录，可能的原因："
echo "1. 请求没有到达服务器（Nginx 配置问题）"
echo "2. 请求被 Nginx 拦截（文件大小限制等）"
echo "3. 浏览器端请求失败（网络问题、CORS 等）"
echo ""
echo "建议："
echo "1. 打开浏览器开发者工具（F12），查看 Network 标签"
echo "2. 重新上传文档，查看请求是否发送成功"
echo "3. 查看浏览器控制台是否有错误信息"
echo ""

