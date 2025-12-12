#!/bin/bash

# 诊断检测日志没有输出的问题

echo "=========================================="
echo "诊断检测日志没有输出的问题"
echo "=========================================="
echo ""

# 1. 检查服务器上的代码是否包含 sys.stderr
echo "1. 检查服务器代码是否包含 sys.stderr..."
echo "请在服务器上执行："
echo "   grep -c 'file=sys.stderr' backend/app/services/document_service.py"
echo "   如果输出是 0，说明代码还没有更新"
echo ""

# 2. 检查服务是否重启
echo "2. 检查服务状态..."
echo "请在服务器上执行："
echo "   sudo systemctl status geshixiugai"
echo "   查看服务启动时间，如果启动时间早于代码更新时间，需要重启"
echo ""

# 3. 检查是否处理过文档
echo "3. 检查是否处理过包含'诚信承诺'和'摘要'的文档..."
echo "   检测日志只在处理文档时才会生成"
echo "   需要在网页上上传一个包含'诚信承诺'和'摘要'的文档"
echo ""

# 4. 检查日志文件权限
echo "4. 检查日志文件..."
echo "请在服务器上执行："
echo "   ls -la /var/log/geshixiugai/error.log"
echo "   确认文件存在且有写入权限"
echo ""

# 5. 检查最近的日志
echo "5. 查看最近的日志（最后30行）..."
echo "请在服务器上执行："
echo "   sudo tail -n 30 /var/log/geshixiugai/error.log"
echo "   查看是否有任何输出"
echo ""

echo "=========================================="
echo "完整排查步骤："
echo "=========================================="
echo ""
echo "步骤1: 确认代码已推送到 GitHub"
echo "  在本地执行: git log --oneline -1"
echo "  查看最新提交是否包含 '修复检测日志输出'"
echo ""
echo "步骤2: 在服务器上拉取最新代码"
echo "  cd /var/www/geshixiugai"
echo "  git pull origin main"
echo ""
echo "步骤3: 验证代码已更新"
echo "  grep -c 'file=sys.stderr' backend/app/services/document_service.py"
echo "  应该输出大于 0 的数字（比如 61）"
echo ""
echo "步骤4: 重启服务"
echo "  sudo systemctl restart geshixiugai"
echo "  sudo systemctl status geshixiugai"
echo ""
echo "步骤5: 上传文档测试"
echo "  在网页上上传一个包含'诚信承诺'和'摘要'的文档"
echo "  等待处理完成"
echo ""
echo "步骤6: 查看检测日志"
echo "  sudo grep '\[检测\]' /var/log/geshixiugai/error.log | tail -n 50"
echo ""

