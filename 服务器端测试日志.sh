#!/bin/bash

# 服务器端测试日志输出

cd /var/www/geshixiugai

echo "=========================================="
echo "测试日志输出功能"
echo "=========================================="
echo ""

# 1. 检查代码是否包含 _log_to_file 方法
echo "1. 检查代码是否包含 _log_to_file 方法..."
if grep -q "_log_to_file" backend/app/services/document_service.py; then
    echo "   ✅ 找到 _log_to_file 方法"
else
    echo "   ❌ 未找到 _log_to_file 方法，代码可能还没有更新"
    echo "   请执行: git pull origin main"
    exit 1
fi
echo ""

# 2. 测试直接写入日志文件
echo "2. 测试直接写入日志文件..."
TEST_MSG="[测试] $(date '+%Y-%m-%d %H:%M:%S') 这是一条测试日志消息"
echo "$TEST_MSG" | sudo tee -a /var/log/geshixiugai/error.log > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ 成功写入日志文件"
    echo "   测试消息: $TEST_MSG"
else
    echo "   ❌ 写入日志文件失败，检查权限"
    exit 1
fi
echo ""

# 3. 检查日志文件中的测试消息
echo "3. 检查日志文件中的测试消息..."
if sudo grep -q "\[测试\]" /var/log/geshixiugai/error.log | tail -1; then
    echo "   ✅ 找到测试消息"
    sudo grep "\[测试\]" /var/log/geshixiugai/error.log | tail -1
else
    echo "   ⚠️  未找到测试消息"
fi
echo ""

# 4. 检查检测日志
echo "4. 检查检测日志..."
DETECT_COUNT=$(sudo grep -c "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null | tr -d '\n' || echo "0")
echo "   找到 $DETECT_COUNT 条检测日志"
if [ "$DETECT_COUNT" != "0" ] && [ "$DETECT_COUNT" -gt 0 ] 2>/dev/null; then
    echo "   ✅ 有检测日志"
    echo "   最近的检测日志（最后3条）:"
    sudo grep "\[检测\]" /var/log/geshixiugai/error.log | tail -3 | sed 's/^/      /'
else
    echo "   ⚠️  没有检测日志"
    echo "   可能的原因："
    echo "     1. 还没有处理过包含'诚信承诺'和'摘要'的文档"
    echo "     2. 服务还没有重启（代码更新后需要重启）"
    echo "     3. 处理文档时出现了错误"
fi
echo ""

# 5. 检查服务状态
echo "5. 检查服务状态..."
if systemctl is-active --quiet geshixiugai; then
    SERVICE_START=$(systemctl show geshixiugai -p ActiveEnterTimestamp --value 2>/dev/null || echo "未知")
    echo "   ✅ 服务正在运行"
    echo "   启动时间: $SERVICE_START"
    echo "   如果代码刚更新，请重启服务: sudo systemctl restart geshixiugai"
else
    echo "   ❌ 服务未运行"
    echo "   请执行: sudo systemctl restart geshixiugai"
fi
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "如果还是没有检测日志，请："
echo "1. 确认代码已更新: git pull origin main"
echo "2. 重启服务: sudo systemctl restart geshixiugai"
echo "3. 在网页上上传一个包含'诚信承诺'和'摘要'的文档"
echo "4. 等待文档处理完成后再查看日志"
echo ""

