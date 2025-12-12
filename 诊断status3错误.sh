#!/bin/bash

# 诊断 status=3 错误的脚本

echo "=========================================="
echo "诊断 status=3/NOTIMPLEMENTED 错误"
echo "=========================================="
echo ""

# 1. 检查日志目录
echo "1. 检查日志目录..."
LOG_DIR="/var/log/geshixiugai"
if [ ! -d "$LOG_DIR" ]; then
    echo "❌ 日志目录不存在: $LOG_DIR"
    echo "   正在创建..."
    sudo mkdir -p "$LOG_DIR"
    sudo chown nginx:nginx "$LOG_DIR" 2>/dev/null || sudo chown www-data:www-data "$LOG_DIR" 2>/dev/null || sudo chown admin:admin "$LOG_DIR"
    sudo chmod 755 "$LOG_DIR"
    echo "✅ 日志目录已创建"
else
    echo "✅ 日志目录存在: $LOG_DIR"
    ls -ld "$LOG_DIR"
fi
echo ""

# 2. 检查项目目录
echo "2. 检查项目目录..."
PROJECT_DIR="/var/www/geshixiugai"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    exit 1
else
    echo "✅ 项目目录存在: $PROJECT_DIR"
fi
echo ""

# 3. 检查虚拟环境
echo "3. 检查虚拟环境..."
VENV_DIR="$PROJECT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ 虚拟环境不存在: $VENV_DIR"
    exit 1
else
    echo "✅ 虚拟环境存在: $VENV_DIR"
fi
echo ""

# 4. 检查关键依赖
echo "4. 检查关键依赖..."
cd "$PROJECT_DIR"
source venv/bin/activate

echo "检查 gunicorn..."
if python -c "import gunicorn" 2>/dev/null; then
    echo "✅ gunicorn 已安装"
else
    echo "❌ gunicorn 未安装"
    echo "   正在安装..."
    pip install gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

echo "检查 uvicorn..."
if python -c "import uvicorn" 2>/dev/null; then
    echo "✅ uvicorn 已安装"
else
    echo "❌ uvicorn 未安装"
    echo "   正在安装..."
    pip install uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

echo "检查 fastapi..."
if python -c "import fastapi" 2>/dev/null; then
    echo "✅ fastapi 已安装"
else
    echo "❌ fastapi 未安装"
    echo "   正在安装..."
    pip install fastapi -i https://pypi.tuna.tsinghua.edu.cn/simple
fi
echo ""

# 5. 测试应用导入
echo "5. 测试应用导入..."
echo "执行: python -c 'from backend.app.main import app; print(\"✅ 应用导入成功\")'"
if python -c "from backend.app.main import app; print('✅ 应用导入成功')" 2>&1; then
    echo "✅ 应用导入成功"
else
    echo "❌ 应用导入失败"
    echo ""
    echo "详细错误信息："
    python -c "from backend.app.main import app; print('✅ 应用导入成功')" 2>&1
    echo ""
    echo "请检查上述错误信息并修复"
    exit 1
fi
echo ""

# 6. 检查 gunicorn_config.py
echo "6. 检查 gunicorn_config.py..."
if [ -f "$PROJECT_DIR/gunicorn_config.py" ]; then
    echo "✅ gunicorn_config.py 存在"
    # 检查日志路径
    if grep -q "/var/log/geshixiugai" "$PROJECT_DIR/gunicorn_config.py"; then
        echo "✅ 日志路径配置正确"
    else
        echo "⚠️ 日志路径可能不正确"
    fi
else
    echo "❌ gunicorn_config.py 不存在"
    exit 1
fi
echo ""

# 7. 测试 Gunicorn 启动（短暂测试）
echo "7. 测试 Gunicorn 启动（5秒超时）..."
echo "执行: timeout 5 gunicorn -c gunicorn_config.py backend.app.main:app"
timeout 5 gunicorn -c gunicorn_config.py backend.app.main:app 2>&1 &
GUNICORN_PID=$!
sleep 2
if ps -p $GUNICORN_PID > /dev/null 2>&1; then
    echo "✅ Gunicorn 可以启动"
    kill $GUNICORN_PID 2>/dev/null
    wait $GUNICORN_PID 2>/dev/null
else
    echo "❌ Gunicorn 启动失败"
    echo "   请查看上面的错误信息"
    exit 1
fi
echo ""

# 8. 检查 systemd 服务文件
echo "8. 检查 systemd 服务文件..."
if [ -f "/etc/systemd/system/geshixiugai.service" ]; then
    echo "✅ 服务文件存在"
    echo ""
    echo "服务文件内容："
    cat /etc/systemd/system/geshixiugai.service
else
    echo "❌ 服务文件不存在"
    exit 1
fi
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果所有检查都通过，尝试重启服务："
echo "  sudo systemctl restart geshixiugai"
echo "  sudo systemctl status geshixiugai"
echo ""

deactivate



