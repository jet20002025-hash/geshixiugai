#!/bin/bash

# 查看 Word转PDF 转换日志的脚本

echo "=========================================="
echo "查看 Word转PDF 转换日志"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1. 检查服务状态..."
if sudo systemctl is-active --quiet geshixiugai; then
    echo "✅ 服务正在运行"
else
    echo "❌ 服务未运行"
    echo "   请先启动服务: sudo systemctl start geshixiugai"
    exit 1
fi
echo ""

# 2. 查看最近的日志（不筛选）
echo "2. 查看最近的日志（最后 50 行）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 50 --no-pager
echo "----------------------------------------"
echo ""

# 3. 查看包含 Word转PDF 或 PDF预览 的日志
echo "3. 查看 Word转PDF 相关日志（最后 100 行）..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 500 --no-pager | grep -E "\[Word转PDF\]|\[PDF预览\]" | tail -n 50
echo "----------------------------------------"
echo ""

# 4. 如果没有相关日志，说明还没有触发转换
if [ $? -ne 0 ] || [ -z "$(sudo journalctl -u geshixiugai -n 500 --no-pager | grep -E '\[Word转PDF\]|\[PDF预览\]')" ]; then
    echo "⚠️ 没有找到 Word转PDF 相关日志"
    echo ""
    echo "可能的原因："
    echo "1. 还没有在网页上触发转换操作"
    echo "2. 日志被清空了"
    echo ""
    echo "下一步操作："
    echo "1. 访问: https://www.geshixiugai.cn/web/convert.html"
    echo "2. 上传一个 Word 文档"
    echo "3. 点击'开始转换'"
    echo "4. 然后重新运行此脚本查看日志"
    echo ""
    echo "或者实时查看日志（在另一个终端窗口）："
    echo "  sudo journalctl -u geshixiugai -f | grep -E '\[Word转PDF\]|\[PDF预览\]'"
    echo ""
fi

echo "=========================================="
echo "查看完成"
echo "=========================================="



