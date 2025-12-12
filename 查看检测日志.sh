#!/bin/bash

# 查看检测日志的便捷脚本

echo "=========================================="
echo "查看检测日志"
echo "=========================================="
echo ""

# 1. 查看最近的检测日志
echo "1. 最近的检测日志（最后30条）:"
echo "----------------------------------------"
sudo grep "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 30 || echo "没有找到检测日志"
echo "----------------------------------------"
echo ""

# 2. 查看PDF分页结果
echo "2. PDF分页结果:"
echo "----------------------------------------"
sudo grep "PDF分页结果\|诚信承诺所在页码\|摘要所在页码\|页码对比" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 20 || echo "没有找到PDF分页结果"
echo "----------------------------------------"
echo ""

# 3. 查看诊断日志
echo "3. 最近的诊断日志（最后20条）:"
echo "----------------------------------------"
sudo grep "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 20 || echo "没有找到诊断日志"
echo "----------------------------------------"
echo ""

# 4. 查看修复日志
echo "4. 最近的修复日志（最后20条）:"
echo "----------------------------------------"
sudo grep "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 20 || echo "没有找到修复日志"
echo "----------------------------------------"
echo ""

# 5. 统计信息
echo "5. 统计信息:"
DETECT_COUNT=$(sudo grep -c "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
DIAGNOSE_COUNT=$(sudo grep -c "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
FIX_COUNT=$(sudo grep -c "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
echo "   检测日志总数: $DETECT_COUNT"
echo "   诊断日志总数: $DIAGNOSE_COUNT"
echo "   修复日志总数: $FIX_COUNT"
echo ""

echo "=========================================="
echo "查看完成"
echo "=========================================="
echo ""
echo "提示："
echo "  - 实时查看: sudo tail -f /var/log/geshixiugai/error.log | grep \"\[检测\]\""
echo "  - 查看今天: sudo grep \"\[检测\]\" /var/log/geshixiugai/error.log | grep \"\$(date '+%Y-%m-%d')\""
echo ""

