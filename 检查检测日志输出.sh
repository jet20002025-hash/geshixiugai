#!/bin/bash

# 检查检测日志输出脚本
# 用于排查为什么没有检测日志输出

echo "=========================================="
echo "检查检测日志输出"
echo "=========================================="
echo ""

# 1. 检查代码是否已更新
echo "1. 检查代码中的检测标记数量..."
DETECT_COUNT=$(grep -c "\[检测\]" backend/app/services/document_service.py 2>/dev/null || echo "0")
DIAGNOSE_COUNT=$(grep -c "\[诊断\]" backend/app/services/document_service.py 2>/dev/null || echo "0")
FIX_COUNT=$(grep -c "\[修复\]" backend/app/services/document_service.py 2>/dev/null || echo "0")

echo "   [检测] 标记数量: $DETECT_COUNT"
echo "   [诊断] 标记数量: $DIAGNOSE_COUNT"
echo "   [修复] 标记数量: $FIX_COUNT"
echo ""

# 2. 检查日志文件是否存在
echo "2. 检查日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    LOG_SIZE=$(stat -f%z /var/log/geshixiugai/error.log 2>/dev/null || stat -c%s /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
    echo "   ✅ 日志文件存在，大小: $LOG_SIZE 字节"
else
    echo "   ❌ 日志文件不存在: /var/log/geshixiugai/error.log"
    echo "   请检查日志文件路径和权限"
    exit 1
fi
echo ""

# 3. 检查日志中的各种标记
echo "3. 检查日志中的标记..."
echo "   [检测] 标记数量:"
sudo grep -c "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "   0"
echo "   [诊断] 标记数量:"
sudo grep -c "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "   0"
echo "   [修复] 标记数量:"
sudo grep -c "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "   0"
echo ""

# 4. 显示最近的日志（最后20行）
echo "4. 最近的日志内容（最后20行）:"
echo "----------------------------------------"
sudo tail -n 20 /var/log/geshixiugai/error.log 2>/dev/null || echo "   无法读取日志文件"
echo "----------------------------------------"
echo ""

# 5. 检查服务状态
echo "5. 检查服务状态..."
if systemctl is-active --quiet geshixiugai; then
    echo "   ✅ 服务正在运行"
    SERVICE_START=$(systemctl show geshixiugai -p ActiveEnterTimestamp --value 2>/dev/null || echo "未知")
    echo "   服务启动时间: $SERVICE_START"
else
    echo "   ❌ 服务未运行"
    echo "   请运行: sudo systemctl restart geshixiugai"
fi
echo ""

# 6. 检查最近的检测日志（如果有）
echo "6. 最近的检测日志（最后10条）:"
echo "----------------------------------------"
sudo grep "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 10 || echo "   没有找到检测日志"
echo "----------------------------------------"
echo ""

# 7. 检查最近的诊断日志（如果有）
echo "7. 最近的诊断日志（最后10条）:"
echo "----------------------------------------"
sudo grep "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null | tail -n 10 || echo "   没有找到诊断日志"
echo "----------------------------------------"
echo ""

# 8. 建议
echo "=========================================="
echo "建议："
echo "=========================================="
if [ "$DETECT_COUNT" -eq "0" ]; then
    echo "❌ 代码中没有检测标记，请先更新代码："
    echo "   git pull origin main"
    echo ""
fi

if [ "$(sudo grep -c "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "0")" -eq "0" ]; then
    echo "⚠️  日志中没有检测输出，可能的原因："
    echo "   1. 服务还没有重启（运行旧代码）"
    echo "      → 执行: sudo systemctl restart geshixiugai"
    echo ""
    echo "   2. 还没有处理过包含'诚信承诺'和'摘要'的文档"
    echo "      → 需要在网页上上传文档并处理"
    echo ""
    echo "   3. 日志输出被缓冲"
    echo "      → 处理文档后等待几秒钟再查看日志"
    echo ""
fi

echo "查看检测日志的命令："
echo "   sudo grep \"\[检测\]\" /var/log/geshixiugai/error.log | tail -n 50"
echo ""
echo "查看诊断日志的命令："
echo "   sudo grep \"\[诊断\]\" /var/log/geshixiugai/error.log | tail -n 50"
echo ""

