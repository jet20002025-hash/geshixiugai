#!/bin/bash

echo "=========================================="
echo "快速修复502 Bad Gateway错误"
echo "=========================================="
echo ""

echo "步骤1: 检查服务状态..."
sudo systemctl status geshixiugai.service | head -n 15

echo ""
echo "步骤2: 检查最近的错误日志..."
sudo tail -n 30 /var/log/geshixiugai/error.log

echo ""
echo "步骤3: 检查代码语法..."
cd /var/www/geshixiugai
python3 -c "from backend.app.main import app; print('✅ 代码导入成功')" 2>&1

echo ""
echo "步骤4: 如果代码有错误，请查看上面的错误信息"
echo "步骤5: 如果代码正常，尝试重启服务..."
echo "sudo systemctl restart geshixiugai"
echo ""
echo "步骤6: 等待5秒后检查服务状态..."
sleep 5
sudo systemctl status geshixiugai.service | head -n 15

echo ""
echo "步骤7: 检查端口监听..."
sudo netstat -tlnp | grep 8000 || sudo ss -tlnp | grep 8000

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
