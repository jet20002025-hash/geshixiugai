#!/bin/bash

# 诊断 Word转PDF 转换问题的脚本

echo "=========================================="
echo "诊断 Word转PDF 转换问题"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
if sudo systemctl is-active --quiet geshixiugai; then
    echo "✅ 服务正在运行"
    sudo systemctl status geshixiugai --no-pager -l | head -n 10
else
    echo "❌ 服务未运行"
    echo "   请先启动服务: sudo systemctl start geshixiugai"
    exit 1
fi
echo ""

# 2. 查看最近的日志（不筛选）
echo "2. 查看最近的日志（最后 30 行，不筛选）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 30 --no-pager
echo "----------------------------------------"
echo ""

# 3. 检查是否有任何错误
echo "3. 检查是否有错误..."
ERROR_COUNT=$(sudo journalctl -u geshixiugai -n 200 --no-pager | grep -iE "error|exception|traceback|failed" | wc -l)
if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️ 发现 $ERROR_COUNT 条错误日志"
    echo "最近的错误："
    sudo journalctl -u geshixiugai -n 200 --no-pager | grep -iE "error|exception|traceback|failed" | tail -n 5
else
    echo "✅ 没有发现错误日志"
fi
echo ""

# 4. 检查 LibreOffice
echo "4. 检查 LibreOffice..."
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice 已安装: $(which libreoffice)"
    libreoffice --version 2>&1 | head -n 1
else
    echo "❌ LibreOffice 未安装"
    echo "   请安装: sudo yum install -y libreoffice-headless"
fi
echo ""

# 5. 检查端口监听
echo "5. 检查服务端口监听..."
if sudo netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    echo "✅ 端口 8000 正在监听"
    sudo netstat -tlnp 2>/dev/null | grep ":8000"
else
    echo "❌ 端口 8000 未监听"
    echo "   服务可能未正常启动"
fi
echo ""

# 6. 测试本地访问
echo "6. 测试本地访问..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200\|301\|302"; then
    echo "✅ 本地访问正常"
else
    echo "⚠️ 本地访问异常"
    curl -s http://localhost:8000 | head -n 5
fi
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果服务正常运行但没有转换日志，说明："
echo "1. 还没有在网页上触发转换操作"
echo "2. 或者转换请求没有到达服务器"
echo ""
echo "下一步操作："
echo "1. 访问: https://www.geshixiugai.cn/web/convert.html"
echo "2. 上传一个 Word 文档 (.docx)"
echo "3. 点击'开始转换'"
echo "4. 然后重新运行此脚本或查看日志："
echo "   sudo journalctl -u geshixiugai -f | grep -E '\[Word转PDF\]|\[PDF预览\]'"
echo ""



