#!/bin/bash

# 查看诊断结果的便捷脚本

echo "=========================================="
echo "查看诊断结果"
echo "=========================================="
echo ""

# 1. 查看原始文档诊断
echo "1. 原始文档诊断结果:"
echo "----------------------------------------"
sudo grep "\[诊断\].*原始文档" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 10 || echo "没有找到原始文档诊断"
echo "----------------------------------------"
echo ""

# 2. 查看格式修改后诊断
echo "2. 格式修改后诊断结果:"
echo "----------------------------------------"
sudo grep "\[诊断\].*格式修改后" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 10 || echo "没有找到格式修改后诊断"
echo "----------------------------------------"
echo ""

# 3. 查看预览文档诊断
echo "3. 预览文档诊断结果:"
echo "----------------------------------------"
sudo grep "\[诊断\].*预览文档" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 10 || echo "没有找到预览文档诊断"
echo "----------------------------------------"
echo ""

# 4. 查看PDF检测结果
echo "4. PDF检测结果:"
echo "----------------------------------------"
sudo grep "\[检测\].*PDF\|\[检测\].*页码" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 20 || echo "没有找到PDF检测结果"
echo "----------------------------------------"
echo ""

# 5. 查看修复结果
echo "5. 修复结果:"
echo "----------------------------------------"
sudo grep "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 20 || echo "没有找到修复结果"
echo "----------------------------------------"
echo ""

# 6. 查看最近的完整诊断流程（最后处理的一个文档）
echo "6. 最近的完整诊断流程:"
echo "----------------------------------------"
# 查找最近的"开始诊断"标记，然后显示后续的50行
LAST_DIAGNOSE=$(sudo grep -n "\[诊断\].*开始诊断" /var/log/geshixiugai/error.log 2>/dev/null | tail -1 | cut -d: -f1)
if [ -n "$LAST_DIAGNOSE" ]; then
    sudo sed -n "${LAST_DIAGNOSE},$((LAST_DIAGNOSE+100))p" /var/log/geshixiugai/error.log 2>/dev/null | grep "\[诊断\]\|\[检测\]\|\[修复\]" | head -n 50
else
    echo "没有找到诊断流程"
fi
echo "----------------------------------------"
echo ""

# 7. 统计信息
echo "7. 统计信息:"
DIAGNOSE_COUNT=$(sudo grep -c "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
DETECT_COUNT=$(sudo grep -c "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
FIX_COUNT=$(sudo grep -c "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
echo "   诊断日志总数: $DIAGNOSE_COUNT"
echo "   检测日志总数: $DETECT_COUNT"
echo "   修复日志总数: $FIX_COUNT"
echo ""

echo "=========================================="
echo "查看完成"
echo "=========================================="
echo ""
echo "提示："
echo "  - 查看所有诊断: sudo grep \"\[诊断\]\" /var/log/geshixiugai/error.log | tail -n 100"
echo "  - 实时查看: sudo tail -f /var/log/geshixiugai/error.log | grep \"\[诊断\]\""
echo "  - 查看今天: sudo grep \"\[诊断\]\" /var/log/geshixiugai/error.log | grep \"\$(date '+%Y-%m-%d')\""
echo ""

