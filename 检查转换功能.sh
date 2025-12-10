#!/bin/bash

# 检查转换功能的脚本

echo "=========================================="
echo "检查 Word转PDF 转换功能"
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

# 2. 检查 LibreOffice
echo "2. 检查 LibreOffice..."
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice 已安装: $(which libreoffice)"
    libreoffice --version 2>&1 | head -n 1
else
    echo "❌ LibreOffice 未安装"
    echo "   请安装: sudo yum install -y libreoffice-headless"
fi
echo ""

# 3. 检查应用日志（查找转换相关的）
echo "3. 查看转换相关的日志..."
echo "搜索关键词: [Word转PDF], [PDF预览], convert-to-pdf"
CONVERT_LOGS=$(sudo journalctl -u geshixiugai -n 500 --no-pager | grep -iE "\[Word转PDF\]|\[PDF预览\]|convert-to-pdf" | tail -n 20)
if [ -n "$CONVERT_LOGS" ]; then
    echo "✅ 找到转换相关的日志："
    echo "$CONVERT_LOGS"
else
    echo "⚠️ 没有找到转换相关的日志"
    echo "   说明还没有触发转换操作，或者请求没有到达服务器"
fi
echo ""

# 4. 查看 Nginx 访问日志（检查是否有请求到达）
echo "4. 查看 Nginx 访问日志（检查转换请求）..."
if [ -f "/var/log/nginx/geshixiugai_access.log" ]; then
    echo "✅ Nginx 访问日志存在"
    echo "最近的转换请求（最后 10 条）："
    sudo tail -n 100 /var/log/nginx/geshixiugai_access.log | grep -iE "convert|POST.*documents" | tail -n 10
else
    echo "⚠️ Nginx 访问日志不存在"
    echo "   检查其他 Nginx 日志..."
    ls -la /var/log/nginx/*access*.log 2>/dev/null | head -n 3
fi
echo ""

# 5. 查看应用错误日志
echo "5. 查看应用错误日志..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    ERROR_COUNT=$(sudo tail -n 100 /var/log/geshixiugai/error.log | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "✅ 错误日志文件存在，有 $ERROR_COUNT 行"
        echo "最近的错误（最后 20 行）："
        sudo tail -n 20 /var/log/geshixiugai/error.log
    else
        echo "✅ 错误日志文件存在，但没有错误"
    fi
else
    echo "⚠️ 错误日志文件不存在"
fi
echo ""

# 6. 检查应用日志文件权限
echo "6. 检查日志目录权限..."
if [ -d "/var/log/geshixiugai" ]; then
    echo "✅ 日志目录存在"
    ls -ld /var/log/geshixiugai
    echo ""
    echo "日志文件："
    ls -lh /var/log/geshixiugai/ 2>/dev/null
else
    echo "⚠️ 日志目录不存在"
    echo "   创建日志目录..."
    sudo mkdir -p /var/log/geshixiugai
    sudo chown nginx:nginx /var/log/geshixiugai 2>/dev/null || sudo chown www-data:www-data /var/log/geshixiugai 2>/dev/null
    sudo chmod 755 /var/log/geshixiugai
    echo "✅ 日志目录已创建"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果所有检查都通过，可以："
echo "1. 访问: https://www.geshixiugai.cn/web/convert.html"
echo "2. 上传一个 Word 文档 (.docx)"
echo "3. 点击'开始转换'"
echo ""
echo "然后实时查看日志："
echo "  sudo journalctl -u geshixiugai -f | grep -E '\[Word转PDF\]|\[PDF预览\]'"
echo ""
echo "或者查看所有日志（不筛选）："
echo "  sudo journalctl -u geshixiugai -f"
echo ""

