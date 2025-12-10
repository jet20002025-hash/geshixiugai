#!/bin/bash

# 检查应用启动状态的脚本

echo "=========================================="
echo "检查应用启动状态"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
sudo systemctl status geshixiugai --no-pager | head -n 15
echo ""

# 2. 检查进程
echo "2. 检查 Gunicorn 进程..."
ps aux | grep gunicorn | grep -v grep
echo ""

# 3. 检查 worker 进程数量
echo "3. 检查 worker 进程..."
WORKER_COUNT=$(ps aux | grep "gunicorn.*backend.app.main:app" | grep -v grep | wc -l)
echo "Worker 进程数量: $WORKER_COUNT"
if [ $WORKER_COUNT -lt 2 ]; then
    echo "⚠️ Worker 进程数量异常（应该至少有 2 个：1 个 master + 1 个 worker）"
else
    echo "✅ Worker 进程数量正常"
fi
echo ""

# 4. 手动测试应用导入
echo "4. 手动测试应用导入..."
cd /var/www/geshixiugai
source venv/bin/activate
echo "执行: python -c 'from backend.app.main import app; print(\"✅ 应用导入成功\")'"
python -c "from backend.app.main import app; print('✅ 应用导入成功')" 2>&1
IMPORT_RESULT=$?
deactivate

if [ $IMPORT_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 应用导入失败！这是问题所在。"
    echo "   请查看上面的错误信息。"
else
    echo "✅ 应用可以正常导入"
fi
echo ""

# 5. 查看应用错误日志文件
echo "5. 查看应用错误日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    ERROR_LINES=$(sudo tail -n 100 /var/log/geshixiugai/error.log | wc -l)
    if [ $ERROR_LINES -gt 0 ]; then
        echo "最近的错误（最后 30 行）："
        sudo tail -n 30 /var/log/geshixiugai/error.log
    else
        echo "⚠️ 错误日志文件为空"
    fi
else
    echo "⚠️ 错误日志文件不存在"
    echo "   检查日志目录..."
    ls -la /var/log/geshixiugai/ 2>/dev/null || echo "   日志目录不存在"
fi
echo ""

# 6. 查看应用访问日志文件
echo "6. 查看应用访问日志文件..."
if [ -f "/var/log/geshixiugai/access.log" ]; then
    echo "✅ 访问日志文件存在"
    ACCESS_LINES=$(sudo tail -n 100 /var/log/geshixiugai/access.log | wc -l)
    if [ $ACCESS_LINES -gt 0 ]; then
        echo "最近的访问（最后 10 行）："
        sudo tail -n 10 /var/log/geshixiugai/access.log
    else
        echo "⚠️ 访问日志文件为空（没有请求）"
    fi
else
    echo "⚠️ 访问日志文件不存在"
fi
echo ""

# 7. 检查日志目录权限
echo "7. 检查日志目录权限..."
if [ -d "/var/log/geshixiugai" ]; then
    echo "✅ 日志目录存在"
    ls -ld /var/log/geshixiugai
    echo ""
    echo "日志文件："
    ls -lh /var/log/geshixiugai/ 2>/dev/null
else
    echo "⚠️ 日志目录不存在，正在创建..."
    sudo mkdir -p /var/log/geshixiugai
    sudo chown nginx:nginx /var/log/geshixiugai 2>/dev/null || sudo chown www-data:www-data /var/log/geshixiugai 2>/dev/null || sudo chown admin:admin /var/log/geshixiugai
    sudo chmod 755 /var/log/geshixiugai
    echo "✅ 日志目录已创建"
fi
echo ""

# 8. 查看最近的 systemd 日志（过滤掉 systemd 消息）
echo "8. 查看应用日志（过滤 systemd 消息）..."
APP_LOGS=$(sudo journalctl -u geshixiugai -n 200 --no-pager | grep -v "systemd\[1\]" | tail -n 30)
if [ -n "$APP_LOGS" ]; then
    echo "✅ 找到应用日志："
    echo "$APP_LOGS"
else
    echo "⚠️ 没有找到应用日志（只有 systemd 消息）"
    echo "   这可能表示应用没有正常启动或没有输出日志"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
if [ $IMPORT_RESULT -ne 0 ]; then
    echo "❌ 应用导入失败，需要修复代码错误"
    echo "   请查看上面的错误信息并修复"
elif [ $WORKER_COUNT -lt 2 ]; then
    echo "⚠️ Worker 进程数量异常，应用可能没有正常启动"
    echo "   请查看错误日志文件"
else
    echo "✅ 应用可以正常导入，Worker 进程正常"
    echo "   如果没有转换日志，说明还没有触发转换操作"
    echo ""
    echo "下一步："
    echo "1. 访问: https://www.geshixiugai.cn/web/convert.html"
    echo "2. 上传 Word 文档并转换"
    echo "3. 查看日志: sudo journalctl -u geshixiugai -f"
fi
echo ""

