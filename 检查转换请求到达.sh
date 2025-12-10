#!/bin/bash

# 检查转换请求是否到达服务器的脚本

echo "=========================================="
echo "检查转换请求是否到达服务器"
echo "=========================================="
echo ""

# 1. 查看应用访问日志（最近的转换请求）
echo "1. 查看应用访问日志（最近的转换请求）..."
echo "----------------------------------------"
sudo tail -n 100 /var/log/geshixiugai/access.log | grep -iE "convert|POST.*documents" | tail -n 10
echo "----------------------------------------"
echo ""

# 2. 查看 Nginx 访问日志（最近的转换请求）
echo "2. 查看 Nginx 访问日志（最近的转换请求）..."
echo "----------------------------------------"
sudo tail -n 100 /var/log/nginx/geshixiugai_access.log 2>/dev/null | grep -iE "convert|POST.*documents" | tail -n 10
if [ $? -ne 0 ]; then
    echo "⚠️ Nginx 访问日志不存在或没有转换请求"
    echo "   检查其他 Nginx 日志..."
    sudo tail -n 50 /var/log/nginx/access.log 2>/dev/null | grep -iE "convert|POST" | tail -n 5
fi
echo "----------------------------------------"
echo ""

# 3. 查看最近的错误日志（查找转换相关）
echo "3. 查看最近的错误日志（查找转换相关）..."
echo "----------------------------------------"
sudo tail -n 200 /var/log/geshixiugai/error.log | grep -iE "\[Word转PDF\]|\[PDF预览\]|convert" | tail -n 20
if [ $? -ne 0 ]; then
    echo "⚠️ 没有找到转换相关的日志"
    echo "   查看最近的错误日志（最后 30 行）："
    sudo tail -n 30 /var/log/geshixiugai/error.log
fi
echo "----------------------------------------"
echo ""

# 4. 检查服务状态
echo "4. 检查服务状态..."
sudo systemctl status geshixiugai --no-pager | head -n 10
echo ""

# 5. 检查代码是否已更新
echo "5. 检查代码是否已更新..."
cd /var/www/geshixiugai
echo "当前代码版本（最后 5 次提交）："
git log --oneline -n 5
echo ""

# 6. 检查是否有未提交的更改
echo "6. 检查是否有未提交的更改..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ 有未提交的更改："
    git status --short
else
    echo "✅ 没有未提交的更改"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果访问日志中没有转换请求，说明："
echo "1. 请求没有到达服务器（可能是 Nginx 配置问题）"
echo "2. 或者请求被拦截了"
echo ""
echo "如果访问日志中有请求但没有错误日志，说明："
echo "1. 代码可能没有更新"
echo "2. 或者日志没有正确输出"
echo ""

