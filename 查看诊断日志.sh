#!/bin/bash

# 查看诊断日志脚本
# 用于查看文档处理过程中的诊断信息

echo "=========================================="
echo "查看诊断日志"
echo "=========================================="
echo ""

# 方法1：查看错误日志中的诊断信息（推荐）
echo "方法1：查看错误日志中的诊断信息（推荐）"
echo "----------------------------------------"
if [ -f "/var/log/geshixiugai/error.log" ]; then
    echo "✅ 错误日志文件存在"
    echo ""
    echo "最近的诊断信息（包含 [诊断] 的行）："
    echo ""
    sudo grep "\[诊断\]" /var/log/geshixiugai/error.log | tail -n 50
    echo ""
    echo "----------------------------------------"
    echo ""
    echo "查看完整的最后100行日志："
    echo ""
    sudo tail -n 100 /var/log/geshixiugai/error.log
else
    echo "⚠️ 错误日志文件不存在: /var/log/geshixiugai/error.log"
    echo "   请检查日志目录是否存在："
    echo "   sudo ls -la /var/log/geshixiugai/"
fi
echo ""

# 方法2：实时查看诊断日志
echo "=========================================="
echo "方法2：实时查看诊断日志（按 Ctrl+C 退出）"
echo "----------------------------------------"
echo "执行命令："
echo "  sudo tail -f /var/log/geshixiugai/error.log | grep '\[诊断\]'"
echo ""
echo "或者查看所有日志（包括诊断）："
echo "  sudo tail -f /var/log/geshixiugai/error.log"
echo ""

# 方法3：查看 systemd 服务日志
echo "=========================================="
echo "方法3：查看 systemd 服务日志"
echo "----------------------------------------"
echo "执行命令："
echo "  sudo journalctl -u geshixiugai -f | grep '\[诊断\]'"
echo ""
echo "或者查看最近的日志："
echo "  sudo journalctl -u geshixiugai -n 200 --no-pager | grep '\[诊断\]'"
echo ""

# 方法4：查看特定文档的诊断信息
echo "=========================================="
echo "方法4：查看特定文档的诊断信息"
echo "----------------------------------------"
echo "如果您知道文档ID，可以搜索特定文档的诊断信息："
echo "  sudo grep '文档ID' /var/log/geshixiugai/error.log | grep '\[诊断\]'"
echo ""

echo "=========================================="
echo "快速查看命令汇总"
echo "=========================================="
echo ""
echo "1. 查看最近的诊断信息："
echo "   sudo grep '\[诊断\]' /var/log/geshixiugai/error.log | tail -n 50"
echo ""
echo "2. 实时查看诊断日志："
echo "   sudo tail -f /var/log/geshixiugai/error.log | grep '\[诊断\]'"
echo ""
echo "3. 查看完整错误日志（最后100行）："
echo "   sudo tail -n 100 /var/log/geshixiugai/error.log"
echo ""
echo "4. 查看 systemd 服务日志中的诊断信息："
echo "   sudo journalctl -u geshixiugai -n 200 --no-pager | grep '\[诊断\]'"
echo ""

