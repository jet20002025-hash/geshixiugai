#!/bin/bash

# 查看 worker 启动错误的脚本

echo "=========================================="
echo "查看 Worker 启动错误"
echo "=========================================="
echo ""

# 1. 查看应用错误日志
echo "1. 查看应用错误日志（最后 50 行）..."
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    echo ""
    echo "最后 50 行错误日志："
    echo "----------------------------------------"
    sudo tail -n 50 /var/log/geshixiugai/error.log
    echo "----------------------------------------"
else
    echo "❌ 错误日志文件不存在: /var/log/geshixiugai/error.log"
    echo "   可能日志目录不存在，正在创建..."
    sudo mkdir -p /var/log/geshixiugai
    sudo chown nginx:nginx /var/log/geshixiugai 2>/dev/null || sudo chown www-data:www-data /var/log/geshixiugai 2>/dev/null || sudo chown admin:admin /var/log/geshixiugai
    sudo chmod 755 /var/log/geshixiugai
fi
echo ""

# 2. 查看访问日志（可能包含错误）
echo "2. 查看访问日志（最后 20 行）..."
if [ -f "/var/log/geshixiugai/access.log" ]; then
    sudo tail -n 20 /var/log/geshixiugai/access.log
else
    echo "访问日志文件不存在"
fi
echo ""

# 3. 手动测试应用导入
echo "3. 手动测试应用导入..."
cd /var/www/geshixiugai
source venv/bin/activate

echo "执行: python -c 'from backend.app.main import app'"
python -c "from backend.app.main import app; print('✅ 应用导入成功')" 2>&1
IMPORT_RESULT=$?

if [ $IMPORT_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 应用导入失败！这是导致 worker 启动失败的原因。"
    echo ""
    echo "详细错误信息："
    python -c "from backend.app.main import app" 2>&1
else
    echo "✅ 应用导入成功"
fi
echo ""

# 4. 测试 UvicornWorker
echo "4. 测试 UvicornWorker..."
if python -c "from uvicorn.workers import UvicornWorker; print('✅ UvicornWorker 可用')" 2>&1; then
    echo "✅ UvicornWorker 可用"
else
    echo "❌ UvicornWorker 不可用"
    echo "   正在安装 uvicorn..."
    pip install uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
fi
echo ""

# 5. 手动测试 Gunicorn 启动（捕获错误）
echo "5. 手动测试 Gunicorn 启动（5秒超时）..."
echo "执行: timeout 5 gunicorn -c gunicorn_config.py backend.app.main:app 2>&1"
timeout 5 gunicorn -c gunicorn_config.py backend.app.main:app 2>&1 | head -n 100
echo ""

deactivate

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果应用导入失败，请检查上面的错误信息并修复。"
echo "如果应用导入成功但 Gunicorn 启动失败，请查看上面的 Gunicorn 错误信息。"
echo ""

