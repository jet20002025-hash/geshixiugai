#!/bin/bash

# 修复连接被拒绝问题

echo "=========================================="
echo "修复连接被拒绝问题"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
sudo systemctl status geshixiugai --no-pager | head -n 25
echo ""

# 2. 检查进程
echo "2. 检查Gunicorn进程..."
ps aux | grep gunicorn | grep -v grep
echo ""

# 3. 检查端口监听
echo "3. 检查端口8000监听..."
sudo netstat -tlnp | grep 8000 || echo "❌ 端口8000未在监听"
echo ""

# 4. 查看详细日志
echo "4. 查看详细日志（最后100行）..."
sudo journalctl -u geshixiugai -n 100 --no-pager | tail -n 100
echo ""

# 5. 检查代码导入
echo "5. 检查代码是否可以正常导入..."
cd /var/www/geshixiugai
source venv/bin/activate

echo "测试应用导入..."
python -c "from backend.app.main import app; print('✅ 应用导入成功')" 2>&1
IMPORT_RESULT=$?

if [ $IMPORT_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 应用导入失败！"
    echo ""
    echo "正在拉取最新代码..."
    git pull origin main
    
    echo ""
    echo "重新测试应用导入..."
    python -c "from backend.app.main import app; print('✅ 应用导入成功')" 2>&1
    IMPORT_RESULT=$?
    
    if [ $IMPORT_RESULT -ne 0 ]; then
        echo ""
        echo "❌ 代码仍有问题！"
        echo ""
        echo "查看详细错误："
        python -c "from backend.app.main import app" 2>&1
        deactivate
        exit 1
    fi
fi

deactivate
echo ""

# 6. 停止服务
echo "6. 停止服务..."
sudo systemctl stop geshixiugai
sleep 2

# 7. 检查是否有残留进程
echo "7. 检查是否有残留进程..."
ps aux | grep gunicorn | grep -v grep
if [ $? -eq 0 ]; then
    echo "发现残留进程，正在清理..."
    sudo pkill -f "gunicorn.*backend.app.main:app"
    sleep 2
fi
echo ""

# 8. 手动测试Gunicorn启动（短暂测试）
echo "8. 手动测试Gunicorn启动（5秒测试）..."
cd /var/www/geshixiugai
source venv/bin/activate

timeout 5 gunicorn -c gunicorn_config.py backend.app.main:app 2>&1 &
GUNICORN_PID=$!
sleep 3

if ps -p $GUNICORN_PID > /dev/null 2>&1; then
    echo "✅ Gunicorn可以启动"
    kill $GUNICORN_PID 2>/dev/null
    wait $GUNICORN_PID 2>/dev/null
else
    echo "❌ Gunicorn启动失败"
    echo "查看启动错误："
    timeout 5 gunicorn -c gunicorn_config.py backend.app.main:app 2>&1 | head -n 50
fi

deactivate
echo ""

# 9. 重启服务
echo "9. 重启服务..."
sudo systemctl start geshixiugai
sleep 5

# 10. 再次检查
echo "10. 再次检查服务状态..."
sudo systemctl status geshixiugai --no-pager | head -n 25
echo ""

echo "11. 检查端口监听..."
sudo netstat -tlnp | grep 8000 || echo "❌ 端口仍未监听"
echo ""

echo "12. 测试连接..."
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://127.0.0.1:8000/docs || echo "❌ 连接失败"
echo ""

echo "=========================================="
echo "修复完成"
echo "=========================================="
echo ""
echo "如果问题仍然存在，请查看上面的详细日志"
echo ""


