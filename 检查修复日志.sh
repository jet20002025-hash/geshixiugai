#!/bin/bash

# 检查修复日志的脚本

echo "=========================================="
echo "检查修复日志"
echo "=========================================="
echo ""

# 1. 查看修复日志
echo "1. 修复日志（最后50条）:"
echo "----------------------------------------"
sudo grep "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 50 || echo "没有找到修复日志"
echo "----------------------------------------"
echo ""

# 2. 查看修复前后的检测日志
echo "2. 修复前后的检测日志:"
echo "----------------------------------------"
sudo grep "修复前检测\|修复后检测" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 20 || echo "没有找到修复前后检测日志"
echo "----------------------------------------"
echo ""

# 3. 查看最近的完整流程
echo "3. 最近的完整流程（诊断+修复+检测）:"
echo "----------------------------------------"
sudo grep "\[诊断\]\|\[修复\]\|\[检测\].*修复" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 100 | head -n 50
echo "----------------------------------------"
echo ""

# 4. 统计
echo "4. 统计信息:"
FIX_COUNT=$(sudo grep -c "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
PRE_FIX_COUNT=$(sudo grep -c "修复前检测" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
POST_FIX_COUNT=$(sudo grep -c "修复后检测" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
echo "   修复日志总数: $FIX_COUNT"
echo "   修复前检测次数: $PRE_FIX_COUNT"
echo "   修复后检测次数: $POST_FIX_COUNT"
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="

