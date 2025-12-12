#!/bin/bash

# 检查文件名问题的诊断脚本

echo "=========================================="
echo "检查文件名问题"
echo "=========================================="
echo ""

# 1. 检查代码是否已更新
echo "1. 检查代码版本..."
echo "----------------------------------------"
cd /var/www/geshixiugai
git log --oneline -n 5
echo ""

# 2. 检查文件名处理代码
echo "2. 检查文件名处理代码..."
echo "----------------------------------------"
grep -A 10 "pdf_filename = Path" backend/app/api/documents.py | head -n 15
echo ""

# 3. 检查服务状态
echo "3. 检查服务状态..."
echo "----------------------------------------"
sudo systemctl status geshixiugai --no-pager | head -n 10
echo ""

# 4. 查看最近的日志
echo "4. 查看最近的转换日志..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 50 --no-pager | grep -E "Word转PDF|文件名|filename" | tail -n 20
echo ""

# 5. 检查错误日志
echo "5. 检查错误日志..."
echo "----------------------------------------"
tail -n 50 /var/log/geshixiugai/error.log | grep -E "Word转PDF|文件名|filename" | tail -n 20
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果代码已更新但文件名仍然不对，请："
echo "1. 确认服务已重启：sudo systemctl restart geshixiugai"
echo "2. 清除浏览器缓存并重新测试"
echo "3. 查看日志中的文件名处理信息"
echo ""



