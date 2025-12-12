#!/bin/bash

# 查看所有日志的脚本（不筛选）

echo "=========================================="
echo "查看所有日志（不筛选）"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
if sudo systemctl is-active --quiet geshixiugai; then
    echo "✅ 服务正在运行"
else
    echo "❌ 服务未运行"
    exit 1
fi
echo ""

# 2. 查看最近的日志（不筛选，最后 50 行）
echo "2. 查看最近的日志（最后 50 行，不筛选）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 50 --no-pager
echo "----------------------------------------"
echo ""

# 3. 查看是否有任何请求日志
echo "3. 查看是否有任何请求日志..."
echo "搜索关键词: POST, GET, convert, document"
sudo journalctl -u geshixiugai -n 200 --no-pager | grep -iE "POST|GET|convert|document|/documents" | tail -n 20
echo ""

# 4. 查看应用日志文件
echo "4. 查看应用日志文件..."
if [ -f "/var/log/geshixiugai/access.log" ]; then
    echo "✅ 访问日志文件存在"
    echo "最近的访问记录（最后 20 行）："
    sudo tail -n 20 /var/log/geshixiugai/access.log
else
    echo "⚠️ 访问日志文件不存在"
fi
echo ""

if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    echo "最近的错误记录（最后 20 行）："
    sudo tail -n 20 /var/log/geshixiugai/error.log
else
    echo "⚠️ 错误日志文件不存在"
fi
echo ""

# 5. 查看 Nginx 日志
echo "5. 查看 Nginx 访问日志..."
if [ -f "/var/log/nginx/geshixiugai_access.log" ]; then
    echo "✅ Nginx 访问日志存在"
    echo "最近的访问记录（最后 20 行）："
    sudo tail -n 20 /var/log/nginx/geshixiugai_access.log | grep -E "convert|POST" | tail -n 10
else
    echo "⚠️ Nginx 访问日志不存在"
fi
echo ""

echo "=========================================="
echo "说明"
echo "=========================================="
echo ""
echo "如果日志中没有转换相关的记录，说明："
echo "1. 还没有在浏览器中触发转换操作"
echo "2. 或者请求没有到达服务器（Nginx 拦截等）"
echo ""
echo "下一步操作："
echo "1. 在浏览器中访问: https://www.geshixiugai.cn/web/convert.html"
echo "2. 上传一个 Word 文档"
echo "3. 点击'开始转换'"
echo "4. 然后重新运行此脚本查看日志"
echo ""
echo "或者实时查看日志（在另一个终端窗口）："
echo "  sudo journalctl -u geshixiugai -f"
echo "  （不筛选，查看所有日志）"
echo ""



