#!/bin/bash

# 查看worker启动错误

echo "=========================================="
echo "查看Worker启动错误"
echo "=========================================="
echo ""

# 1. 停止服务
echo "1. 停止服务..."
sudo systemctl stop geshixiugai
sleep 2
echo ""

# 2. 检查代码导入
echo "2. 检查代码是否可以导入..."
cd /var/www/geshixiugai
source venv/bin/activate

echo "测试应用导入..."
python -c "from backend.app.main import app; print('✅ 应用导入成功')" 2>&1
IMPORT_RESULT=$?

if [ $IMPORT_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 应用导入失败！"
    echo ""
    echo "详细错误信息："
    python -c "from backend.app.main import app" 2>&1
    deactivate
    exit 1
fi

deactivate
echo ""

# 3. 手动测试Gunicorn启动（捕获详细错误）
echo "3. 手动测试Gunicorn启动（捕获详细错误）..."
cd /var/www/geshixiugai
source venv/bin/activate

echo "执行: gunicorn -c gunicorn_config.py backend.app.main:app"
echo "（5秒后自动停止）"
echo ""

timeout 5 gunicorn -c gunicorn_config.py backend.app.main:app 2>&1 | head -n 100

deactivate
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果看到错误信息，请将错误信息发给我"
echo ""
