#!/bin/bash

# 快速修复502 Bad Gateway错误

echo "=========================================="
echo "快速修复502 Bad Gateway错误"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
sudo systemctl status geshixiugai --no-pager | head -n 15
echo ""

# 2. 检查是否有语法错误
echo "2. 检查代码是否有语法错误..."
cd /var/www/geshixiugai
source venv/bin/activate
python -c "from backend.app.main import app; print('✅ 代码导入成功')" 2>&1
IMPORT_RESULT=$?
deactivate

if [ $IMPORT_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 代码导入失败！请查看上面的错误信息。"
    echo "   可能需要回退到上一个版本："
    echo "   cd /var/www/geshixiugai"
    echo "   git log --oneline -5"
    echo "   git reset --hard HEAD~1  # 回退一个版本"
    echo "   sudo systemctl restart geshixiugai"
    exit 1
fi
echo ""

# 3. 查看最近的错误日志
echo "3. 查看最近的错误日志..."
sudo journalctl -u geshixiugai -n 50 --no-pager | tail -n 30
echo ""

# 4. 重启服务
echo "4. 重启服务..."
sudo systemctl restart geshixiugai
sleep 3

# 5. 再次检查服务状态
echo "5. 检查服务是否启动成功..."
sudo systemctl status geshixiugai --no-pager | head -n 15
echo ""

# 6. 测试本地连接
echo "6. 测试本地连接..."
curl -v http://127.0.0.1:8000/docs 2>&1 | head -n 10
echo ""

echo "=========================================="
echo "修复完成"
echo "=========================================="
echo ""
echo "如果服务仍然无法启动，请执行："
echo "  sudo journalctl -u geshixiugai -n 100 --no-pager"
echo "  查看详细错误信息"


