#!/bin/bash

# 排查检测日志没有输出的步骤

echo "=========================================="
echo "排查检测日志没有输出的原因"
echo "=========================================="
echo ""

# 1. 检查日志文件是否存在
echo "1. 检查日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 日志文件存在"
    FILE_SIZE=$(sudo stat -c%s /var/log/geshixiugai/error.log 2>/dev/null || sudo stat -f%z /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
    echo "   文件大小: $FILE_SIZE 字节"
    if [ "$FILE_SIZE" -gt 0 ]; then
        echo "   最后修改时间:"
        sudo ls -lh /var/log/geshixiugai/error.log
    else
        echo "   ⚠️ 日志文件为空"
    fi
else
    echo "❌ 日志文件不存在"
fi
echo ""

# 2. 检查是否有检测标记
echo "2. 检查是否有检测标记..."
DETECT_COUNT=$(sudo grep -c "\[检测\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
echo "   检测标记数量: $DETECT_COUNT"

FIX_COUNT=$(sudo grep -c "\[修复\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
echo "   修复标记数量: $FIX_COUNT"

DIAG_COUNT=$(sudo grep -c "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
echo "   诊断标记数量: $DIAG_COUNT"
echo ""

# 3. 检查代码是否包含检测功能
echo "3. 检查代码是否包含检测功能..."
cd /var/www/geshixiugai 2>/dev/null || cd /var/www/geshixiugai
if [ -f "backend/app/services/document_service.py" ]; then
    DETECT_IN_CODE=$(sudo grep -c "\[检测\]" backend/app/services/document_service.py 2>/dev/null || echo "0")
    echo "   代码中包含检测标记: $DETECT_IN_CODE 处"
    
    FIX_IN_CODE=$(sudo grep -c "\[修复\]" backend/app/services/document_service.py 2>/dev/null || echo "0")
    echo "   代码中包含修复标记: $FIX_IN_CODE 处"
    
    if [ "$DETECT_IN_CODE" -eq 0 ]; then
        echo "   ❌ 代码中不包含检测功能，需要更新代码"
    else
        echo "   ✅ 代码中包含检测功能"
    fi
else
    echo "   ⚠️ 无法找到代码文件"
fi
echo ""

# 4. 检查服务状态
echo "4. 检查服务状态..."
if systemctl is-active --quiet geshixiugai; then
    echo "   ✅ 服务正在运行"
    SERVICE_START=$(sudo systemctl show -p ActiveEnterTimestamp geshixiugai | cut -d= -f2)
    echo "   服务启动时间: $SERVICE_START"
else
    echo "   ❌ 服务未运行"
fi
echo ""

# 5. 查看最近的日志（不筛选）
echo "5. 查看最近的日志（最后20行，不筛选）..."
echo "----------------------------------------"
sudo tail -n 20 /var/log/geshixiugai/error.log 2>/dev/null || echo "无法读取日志文件"
echo "----------------------------------------"
echo ""

# 6. 建议操作
echo "=========================================="
echo "建议操作"
echo "=========================================="
echo ""

if [ "$DETECT_IN_CODE" -eq 0 ]; then
    echo "1. 更新代码:"
    echo "   cd /var/www/geshixiugai"
    echo "   git pull origin main"
    echo ""
fi

if [ "$DETECT_COUNT" -eq 0 ]; then
    echo "2. 重启服务:"
    echo "   sudo systemctl restart geshixiugai"
    echo ""
    echo "3. 上传一个文档进行测试（在网页上操作）"
    echo ""
    echo "4. 然后再次查看检测日志:"
    echo "   sudo grep \"\[检测\]\" /var/log/geshixiugai/error.log | tail -n 50"
fi
echo ""

