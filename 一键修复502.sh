#!/bin/bash

echo "=========================================="
echo "一键修复502 Bad Gateway错误"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
sudo systemctl status geshixiugai.service | head -n 15

# 2. 查看错误日志
echo ""
echo "2. 查看最近的错误日志..."
sudo tail -n 30 /var/log/geshixiugai/error.log | tail -n 20

# 3. 检查代码语法
echo ""
echo "3. 检查代码语法..."
cd /var/www/geshixiugai 2>/dev/null || cd "$(dirname "$0")"
if python3 -c "from backend.app.main import app; print('✅ 代码导入成功')" 2>&1; then
    echo "✅ 代码语法正确"
else
    echo "❌ 代码有错误，请查看上面的错误信息"
    exit 1
fi

# 4. 重启服务
echo ""
echo "4. 重启服务..."
sudo systemctl restart geshixiugai

# 5. 等待服务启动
echo ""
echo "5. 等待服务启动（5秒）..."
sleep 5

# 6. 检查服务状态
echo ""
echo "6. 检查服务状态..."
if sudo systemctl is-active --quiet geshixiugai.service; then
    echo "✅ 服务运行正常"
else
    echo "❌ 服务启动失败，查看详细日志："
    sudo journalctl -u geshixiugai.service -n 30 --no-pager
    exit 1
fi

# 7. 检查端口
echo ""
echo "7. 检查端口8000..."
if sudo netstat -tlnp 2>/dev/null | grep 8000 || sudo ss -tlnp 2>/dev/null | grep 8000; then
    echo "✅ 端口8000正在监听"
else
    echo "❌ 端口8000未监听"
fi

# 8. 测试连接
echo ""
echo "8. 测试本地连接..."
if curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
    echo "✅ 本地连接成功"
else
    echo "❌ 本地连接失败"
fi

echo ""
echo "=========================================="
echo "修复完成"
echo "=========================================="
echo ""
echo "如果问题仍然存在，请运行："
echo "  sudo journalctl -u geshixiugai.service -n 50 --no-pager"
echo "查看详细错误信息"

