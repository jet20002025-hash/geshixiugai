#!/bin/bash

# 服务器端快速检查脚本
# 在服务器上执行此脚本来诊断检测日志问题

cd /var/www/geshixiugai

echo "=========================================="
echo "服务器端快速检查"
echo "=========================================="
echo ""

# 1. 检查代码是否包含 sys.stderr
echo "1. 检查代码是否包含 sys.stderr..."
SYS_STDERR_COUNT=$(grep -c 'file=sys.stderr' backend/app/services/document_service.py 2>/dev/null || echo "0")
echo "   找到 $SYS_STDERR_COUNT 处使用 sys.stderr"
if [ "$SYS_STDERR_COUNT" -eq "0" ]; then
    echo "   ❌ 代码还没有更新！需要执行: git pull origin main"
else
    echo "   ✅ 代码已更新"
fi
echo ""

# 2. 检查服务状态
echo "2. 检查服务状态..."
if systemctl is-active --quiet geshixiugai; then
    SERVICE_START=$(systemctl show geshixiugai -p ActiveEnterTimestamp --value 2>/dev/null || echo "未知")
    echo "   ✅ 服务正在运行"
    echo "   启动时间: $SERVICE_START"
    echo "   建议：如果代码刚更新，请重启服务: sudo systemctl restart geshixiugai"
else
    echo "   ❌ 服务未运行"
    echo "   请执行: sudo systemctl restart geshixiugai"
fi
echo ""

# 3. 检查日志文件
echo "3. 检查日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    LOG_SIZE=$(stat -c%s /var/log/geshixiugai/error.log 2>/dev/null || stat -f%z /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
    echo "   ✅ 日志文件存在，大小: $LOG_SIZE 字节"
    
    # 检查最近的日志
    echo "   最近的日志（最后5行）:"
    sudo tail -n 5 /var/log/geshixiugai/error.log 2>/dev/null | sed 's/^/      /' || echo "      (无法读取)"
else
    echo "   ❌ 日志文件不存在: /var/log/geshixiugai/error.log"
fi
echo ""

# 4. 检查检测日志
echo "4. 检查检测日志..."
DETECT_COUNT=$(sudo grep -c "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
DETECT_COUNT=${DETECT_COUNT:-0}
echo "   找到 $DETECT_COUNT 条检测日志"
if [ "$DETECT_COUNT" = "0" ] || [ "$DETECT_COUNT" -eq 0 ] 2>/dev/null; then
    echo "   ⚠️  没有检测日志"
    echo "   可能的原因："
    echo "     1. 代码还没有更新（检查步骤1）"
    echo "     2. 服务还没有重启（检查步骤2）"
    echo "     3. 还没有处理过包含'诚信承诺'和'摘要'的文档"
    echo "        → 需要在网页上上传文档并处理"
else
    echo "   ✅ 有检测日志"
    echo "   最近的检测日志（最后3条）:"
    sudo grep "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 3 | sed 's/^/      /' || echo "      (无法读取)"
fi
echo ""

# 5. 检查诊断日志
echo "5. 检查诊断日志..."
DIAGNOSE_COUNT=$(sudo grep -c "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
DIAGNOSE_COUNT=${DIAGNOSE_COUNT:-0}
echo "   找到 $DIAGNOSE_COUNT 条诊断日志"
echo ""

# 6. 检查修复日志
echo "6. 检查修复日志..."
FIX_COUNT=$(sudo grep -c "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
FIX_COUNT=${FIX_COUNT:-0}
echo "   找到 $FIX_COUNT 条修复日志"
echo ""

# 7. 总结和建议
echo "=========================================="
echo "总结和建议"
echo "=========================================="
echo ""

if [ "$SYS_STDERR_COUNT" -eq "0" ]; then
    echo "❌ 代码还没有更新"
    echo "   执行: git pull origin main"
    echo "   然后: sudo systemctl restart geshixiugai"
    echo ""
fi

if ([ "$DETECT_COUNT" = "0" ] || [ "$DETECT_COUNT" -eq 0 ] 2>/dev/null) && [ "$SYS_STDERR_COUNT" -gt "0" ]; then
    echo "⚠️  代码已更新，但没有检测日志"
    echo "   可能的原因："
    echo "   1. 服务还没有重启 → sudo systemctl restart geshixiugai"
    echo "   2. 还没有处理过文档 → 在网页上上传文档并处理"
    echo ""
fi

if [ "$DETECT_COUNT" != "0" ] && [ "$DETECT_COUNT" -gt 0 ] 2>/dev/null; then
    echo "✅ 检测日志正常输出"
    echo "   查看完整日志: sudo grep '\[检测\]' /var/log/geshixiugai/error.log | tail -n 50"
    echo ""
fi

echo "查看检测日志的命令："
echo "   sudo grep \"\[检测\]\" /var/log/geshixiugai/error.log | tail -n 50"
echo ""

