#!/bin/bash

# 检查应用是否正常启动的脚本

echo "=========================================="
echo "检查应用是否正常启动"
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

# 3. 检查端口监听
echo "3. 检查端口监听..."
sudo netstat -tlnp 2>/dev/null | grep 8000 || sudo ss -tlnp | grep 8000
echo ""

# 4. 测试本地访问
echo "4. 测试本地访问..."
echo "执行: curl -v http://localhost:8000/ 2>&1 | head -n 30"
curl -v http://localhost:8000/ 2>&1 | head -n 30
echo ""

# 5. 查看应用启动日志（过滤掉 systemd）
echo "5. 查看应用启动日志（最近 100 行，过滤 systemd）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 100 --no-pager | grep -v "systemd\[1\]" | tail -n 50
echo "----------------------------------------"
echo ""

# 6. 检查应用错误日志文件
echo "6. 检查应用错误日志文件..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    echo "最近的错误（最后 30 行）："
    sudo tail -n 30 /var/log/geshixiugai/error.log
else
    echo "⚠️ 错误日志文件不存在"
    echo "   检查日志目录..."
    ls -la /var/log/geshixiugai/ 2>/dev/null || echo "   日志目录不存在"
fi
echo ""

# 7. 手动测试应用导入
echo "7. 手动测试应用导入..."
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

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
if [ $IMPORT_RESULT -ne 0 ]; then
    echo "⚠️ 应用导入失败，需要修复代码错误"
    echo "   请查看上面的错误信息并修复"
else
    echo "✅ 应用可以正常导入"
    echo "   如果服务仍然无法响应，可能是："
    echo "   1. 服务配置问题"
    echo "   2. 权限问题"
    echo "   3. 端口绑定问题"
fi
echo ""

