#!/bin/bash

# 检查应用响应的脚本

echo "=========================================="
echo "检查应用响应"
echo "=========================================="
echo ""

# 1. 测试根路径
echo "1. 测试根路径 (/)..."
echo "执行: curl -v http://localhost:8000/"
curl -v http://localhost:8000/ 2>&1 | head -n 20
echo ""

# 2. 测试健康检查
echo "2. 测试健康检查 (/docs)..."
echo "执行: curl -s http://localhost:8000/docs | head -n 5"
curl -s http://localhost:8000/docs 2>&1 | head -n 5
echo ""

# 3. 测试 API 端点
echo "3. 测试 API 端点 (/documents/convert-to-pdf)..."
echo "执行: curl -X POST http://localhost:8000/documents/convert-to-pdf"
curl -X POST http://localhost:8000/documents/convert-to-pdf 2>&1 | head -n 10
echo ""

# 4. 查看应用日志（最近的）
echo "4. 查看应用日志（最近 50 行）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 50 --no-pager | grep -v "systemd\[1\]" | tail -n 30
echo "----------------------------------------"
echo ""

# 5. 检查应用错误日志文件
echo "5. 检查应用错误日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    echo "最近的错误（最后 20 行）："
    sudo tail -n 20 /var/log/geshixiugai/error.log
else
    echo "⚠️ 错误日志文件不存在: /var/log/geshixiugai/error.log"
    echo "   检查日志目录..."
    ls -la /var/log/geshixiugai/ 2>/dev/null || echo "   日志目录不存在"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="

