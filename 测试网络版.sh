#!/bin/bash

# 测试网络版应用的脚本

echo "=========================================="
echo "测试网络版应用"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
if sudo systemctl is-active --quiet geshixiugai; then
    echo "✅ 服务正在运行"
else
    echo "❌ 服务未运行，正在启动..."
    sudo systemctl start geshixiugai
    sleep 3
fi
echo ""

# 2. 测试本地访问
echo "2. 测试本地访问..."
echo "执行: curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/"
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/ 2>&1)
echo "HTTP 状态码: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ 本地访问正常"
else
    echo "❌ 本地访问异常，状态码: $HTTP_CODE"
    echo "   详细响应："
    curl -v http://localhost:8000/ 2>&1 | head -n 20
fi
echo ""

# 3. 测试 API 文档
echo "3. 测试 API 文档..."
echo "执行: curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs"
DOCS_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs 2>&1)
echo "HTTP 状态码: $DOCS_CODE"

if [ "$DOCS_CODE" = "200" ]; then
    echo "✅ API 文档可访问"
else
    echo "⚠️ API 文档访问异常，状态码: $DOCS_CODE"
fi
echo ""

# 4. 测试前端页面
echo "4. 测试前端页面..."
echo "执行: curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/web/"
WEB_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/web/ 2>&1)
echo "HTTP 状态码: $WEB_CODE"

if [ "$WEB_CODE" = "200" ] || [ "$WEB_CODE" = "301" ] || [ "$WEB_CODE" = "302" ]; then
    echo "✅ 前端页面可访问"
else
    echo "⚠️ 前端页面访问异常，状态码: $WEB_CODE"
fi
echo ""

# 5. 测试转换页面
echo "5. 测试转换页面..."
echo "执行: curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/web/convert.html"
CONVERT_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/web/convert.html 2>&1)
echo "HTTP 状态码: $CONVERT_CODE"

if [ "$CONVERT_CODE" = "200" ]; then
    echo "✅ 转换页面可访问"
else
    echo "⚠️ 转换页面访问异常，状态码: $CONVERT_CODE"
fi
echo ""

# 6. 检查应用日志（最近的）
echo "6. 查看应用日志（最近 20 行，过滤 systemd）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 50 --no-pager | grep -v "systemd\[1\]" | tail -n 20
echo "----------------------------------------"
echo ""

# 7. 检查错误日志
echo "7. 检查错误日志..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    ERROR_COUNT=$(sudo tail -n 100 /var/log/geshixiugai/error.log | grep -iE "error|exception" | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "⚠️ 发现 $ERROR_COUNT 条错误"
        echo "最近的错误："
        sudo tail -n 100 /var/log/geshixiugai/error.log | grep -iE "error|exception" | tail -n 5
    else
        echo "✅ 没有发现错误"
    fi
else
    echo "⚠️ 错误日志文件不存在"
fi
echo ""

# 8. 检查 LibreOffice
echo "8. 检查 LibreOffice..."
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice 已安装: $(which libreoffice)"
    libreoffice --version 2>&1 | head -n 1
else
    echo "❌ LibreOffice 未安装"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "如果所有检查都通过，可以："
echo "1. 访问: https://www.geshixiugai.cn"
echo "2. 访问: https://www.geshixiugai.cn/web/convert.html"
echo "3. 上传 Word 文档测试转换功能"
echo ""
echo "如果发现问题，请查看上面的错误信息"
echo ""

