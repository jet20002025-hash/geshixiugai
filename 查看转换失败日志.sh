#!/bin/bash

# 查看转换失败详细日志的脚本

echo "=========================================="
echo "查看转换失败详细日志"
echo "=========================================="
echo ""

# 1. 查看应用错误日志文件（最重要的）
echo "1. 查看应用错误日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    echo "最近的错误（最后 50 行）："
    echo "----------------------------------------"
    sudo tail -n 50 /var/log/geshixiugai/error.log
    echo "----------------------------------------"
else
    echo "❌ 错误日志文件不存在: /var/log/geshixiugai/error.log"
    echo "   检查日志目录..."
    ls -la /var/log/geshixiugai/ 2>/dev/null || echo "   日志目录不存在"
fi
echo ""

# 2. 查看应用访问日志
echo "2. 查看应用访问日志..."
if [ -f "/var/log/geshixiugai/access.log" ]; then
    echo "✅ 访问日志文件存在"
    echo "最近的访问（最后 20 行）："
    sudo tail -n 20 /var/log/geshixiugai/access.log
else
    echo "⚠️ 访问日志文件不存在"
fi
echo ""

# 3. 查看 Nginx 访问日志（检查请求是否到达）
echo "3. 查看 Nginx 访问日志（检查转换请求）..."
if [ -f "/var/log/nginx/geshixiugai_access.log" ]; then
    echo "✅ Nginx 访问日志存在"
    echo "最近的转换请求（最后 10 条）："
    sudo tail -n 100 /var/log/nginx/geshixiugai_access.log | grep -iE "convert|POST.*documents" | tail -n 10
else
    echo "⚠️ Nginx 访问日志不存在"
    echo "   检查其他 Nginx 日志..."
    sudo tail -n 50 /var/log/nginx/access.log 2>/dev/null | grep -iE "convert|POST" | tail -n 5
fi
echo ""

# 4. 查看 Nginx 错误日志
echo "4. 查看 Nginx 错误日志..."
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

# 5. 在 systemd 日志中搜索转换相关的信息
echo "5. 在 systemd 日志中搜索转换相关信息..."
echo "搜索关键词: Word转PDF, PDF预览, convert, LibreOffice"
CONVERT_LOGS=$(sudo journalctl -u geshixiugai -n 1000 --no-pager | grep -iE "\[Word转PDF\]|\[PDF预览\]|convert|LibreOffice" | tail -n 30)
if [ -n "$CONVERT_LOGS" ]; then
    echo "✅ 找到转换相关的日志："
    echo "$CONVERT_LOGS"
else
    echo "⚠️ 没有找到转换相关的日志"
    echo "   说明应用可能没有输出日志，或者日志没有正确记录"
fi
echo ""

# 6. 检查 LibreOffice 权限
echo "6. 检查 LibreOffice 权限..."
if [ -f "/bin/libreoffice" ]; then
    echo "✅ LibreOffice 文件存在: /bin/libreoffice"
    ls -l /bin/libreoffice
    echo ""
    echo "检查服务运行用户是否能执行..."
    # 获取服务运行用户
    SERVICE_USER=$(ps aux | grep "gunicorn.*backend.app.main:app" | grep -v grep | head -n 1 | awk '{print $1}')
    if [ -n "$SERVICE_USER" ]; then
        echo "服务运行用户: $SERVICE_USER"
        sudo -u $SERVICE_USER /bin/libreoffice --version 2>&1 | head -n 3
    else
        echo "⚠️ 无法确定服务运行用户"
    fi
else
    echo "❌ LibreOffice 文件不存在: /bin/libreoffice"
fi
echo ""

# 7. 检查日志目录权限
echo "7. 检查日志目录权限..."
if [ -d "/var/log/geshixiugai" ]; then
    echo "✅ 日志目录存在"
    ls -ld /var/log/geshixiugai
    echo ""
    echo "日志文件："
    ls -lh /var/log/geshixiugai/ 2>/dev/null
else
    echo "❌ 日志目录不存在"
    echo "   创建日志目录..."
    sudo mkdir -p /var/log/geshixiugai
    sudo chown nginx:nginx /var/log/geshixiugai 2>/dev/null || sudo chown www-data:www-data /var/log/geshixiugai 2>/dev/null || sudo chown admin:admin /var/log/geshixiugai
    sudo chmod 755 /var/log/geshixiugai
    echo "✅ 日志目录已创建"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果错误日志文件中有错误信息，请查看上面的输出。"
echo "如果错误日志文件不存在或为空，可能是日志配置问题。"
echo ""



