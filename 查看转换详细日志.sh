#!/bin/bash

# 查看转换详细日志的脚本

echo "=========================================="
echo "查看转换详细日志"
echo "=========================================="
echo ""

# 1. 查看最近的转换相关日志
echo "1. 查看最近的转换相关日志（最后 200 行，包含 [Word转PDF] 和 [PDF预览]）..."
echo "----------------------------------------"
sudo tail -n 200 /var/log/geshixiugai/error.log | grep -E "\[Word转PDF\]|\[PDF预览\]" | tail -n 50
echo "----------------------------------------"
echo ""

# 2. 查看完整的转换日志（包含上下文）
echo "2. 查看完整的转换日志（包含上下文，最后 500 行）..."
echo "----------------------------------------"
# 查找包含 [Word转PDF] 或 [PDF预览] 的行，并显示前后各 5 行
sudo tail -n 500 /var/log/geshixiugai/error.log | grep -A 5 -B 5 -E "\[Word转PDF\]|\[PDF预览\]" | tail -n 100
echo "----------------------------------------"
echo ""

# 3. 查看最近的错误（所有内容）
echo "3. 查看最近的错误日志（最后 100 行，不筛选）..."
echo "----------------------------------------"
sudo tail -n 100 /var/log/geshixiugai/error.log
echo "----------------------------------------"
echo ""

# 4. 查找 LibreOffice 相关的错误
echo "4. 查找 LibreOffice 相关的错误..."
echo "----------------------------------------"
sudo tail -n 500 /var/log/geshixiugai/error.log | grep -iE "libreoffice|soffice|PDF|转换失败|错误码|错误输出" | tail -n 30
echo "----------------------------------------"
echo ""

# 5. 查看访问日志（确认请求到达）
echo "5. 查看访问日志（确认请求到达）..."
echo "----------------------------------------"
sudo tail -n 50 /var/log/geshixiugai/access.log | grep -iE "convert|POST.*documents" | tail -n 10
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "说明"
echo "=========================================="
echo ""
echo "如果看到以下信息，请特别注意："
echo "1. [PDF预览] LibreOffice返回错误码: XXX - 这是 LibreOffice 的具体错误"
echo "2. [PDF预览] LibreOffice错误输出: ... - 这是 LibreOffice 的详细错误信息"
echo "3. [PDF预览] 文件权限: ... - 检查文件权限是否正确"
echo "4. [PDF预览] 输出目录权限: ... - 检查目录权限是否正确"
echo "5. [PDF预览] 当前用户UID: ... - 检查用户权限"
echo ""
echo "请把上面的输出结果发给我，我会根据具体错误信息进一步修复。"
echo ""



