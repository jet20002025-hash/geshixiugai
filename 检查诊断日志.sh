#!/bin/bash

# 检查诊断日志脚本

echo "=========================================="
echo "检查诊断日志状态"
echo "=========================================="
echo ""

# 1. 检查日志目录是否存在
echo "1. 检查日志目录..."
if [ -d "/var/log/geshixiugai" ]; then
    echo "✅ 日志目录存在: /var/log/geshixiugai"
    ls -ld /var/log/geshixiugai
else
    echo "❌ 日志目录不存在: /var/log/geshixiugai"
    echo "   正在创建..."
    sudo mkdir -p /var/log/geshixiugai
    sudo chown nginx:nginx /var/log/geshixiugai 2>/dev/null || sudo chown www-data:www-data /var/log/geshixiugai 2>/dev/null || sudo chown admin:admin /var/log/geshixiugai
    sudo chmod 755 /var/log/geshixiugai
    echo "✅ 日志目录已创建"
fi
echo ""

# 2. 检查日志文件是否存在
echo "2. 检查日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    FILE_SIZE=$(sudo stat -c%s /var/log/geshixiugai/error.log 2>/dev/null || sudo stat -f%z /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -gt 0 ]; then
        echo "   文件大小: $FILE_SIZE 字节"
        echo "   最后修改时间:"
        sudo ls -lh /var/log/geshixiugai/error.log
        echo ""
        echo "   最后10行内容:"
        sudo tail -n 10 /var/log/geshixiugai/error.log
    else
        echo "   ⚠️ 日志文件为空"
    fi
else
    echo "❌ 错误日志文件不存在"
    echo "   这可能是正常的，如果服务刚启动还没有处理过文档"
fi
echo ""

# 3. 检查是否有诊断信息
echo "3. 检查是否有诊断信息..."
DIAG_COUNT=$(sudo grep -c "\[诊断\]" /var/log/geshixiugai/error.log 2>/dev/null || echo "0")
if [ "$DIAG_COUNT" -gt 0 ]; then
    echo "✅ 找到 $DIAG_COUNT 条诊断信息"
    echo ""
    echo "   最近的诊断信息:"
    sudo grep "\[诊断\]" /var/log/geshixiugai/error.log | tail -n 10
else
    echo "⚠️ 没有找到诊断信息"
    echo "   可能的原因："
    echo "   1. 服务还没有处理过文档"
    echo "   2. 服务还没有重启，新代码还没有运行"
    echo "   3. 日志文件为空"
fi
echo ""

# 4. 检查服务状态
echo "4. 检查服务状态..."
if systemctl is-active --quiet geshixiugai; then
    echo "✅ 服务正在运行"
    SERVICE_START=$(sudo systemctl show -p ActiveEnterTimestamp geshixiugai | cut -d= -f2)
    echo "   服务启动时间: $SERVICE_START"
else
    echo "❌ 服务未运行"
    echo "   请启动服务: sudo systemctl start geshixiugai"
fi
echo ""

# 5. 检查代码是否已更新
echo "5. 检查代码是否包含诊断功能..."
if [ -f "/var/www/geshixiugai/backend/app/services/document_service.py" ]; then
    if sudo grep -q "_diagnose_integrity_abstract_separation" /var/www/geshixiugai/backend/app/services/document_service.py; then
        echo "✅ 代码包含诊断功能"
    else
        echo "❌ 代码不包含诊断功能"
        echo "   需要更新代码: cd /var/www/geshixiugai && git pull origin main"
    fi
else
    echo "⚠️ 无法检查代码文件"
fi
echo ""

# 6. 建议操作
echo "=========================================="
echo "建议操作"
echo "=========================================="
echo ""
if [ "$DIAG_COUNT" -eq 0 ]; then
    echo "1. 确保代码已更新:"
    echo "   cd /var/www/geshixiugai"
    echo "   git pull origin main"
    echo ""
    echo "2. 重启服务:"
    echo "   sudo systemctl restart geshixiugai"
    echo ""
    echo "3. 上传一个文档进行测试"
    echo ""
    echo "4. 然后再次查看诊断日志:"
    echo "   sudo grep '\[诊断\]' /var/log/geshixiugai/error.log | tail -n 50"
fi
echo ""

