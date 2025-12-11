#!/bin/bash

# 查看服务器IP地址和网络信息

echo "=========================================="
echo "查看服务器IP地址和网络信息"
echo "=========================================="
echo ""

# 1. 查看公网IP地址
echo "1. 公网IP地址："
echo "----------------------------------------"
# 方法1：使用curl查询公网IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || curl -s icanhazip.com 2>/dev/null)
if [ -n "$PUBLIC_IP" ]; then
    echo "公网IP: $PUBLIC_IP"
else
    echo "无法获取公网IP（可能需要网络连接）"
fi
echo ""

# 2. 查看内网IP地址
echo "2. 内网IP地址："
echo "----------------------------------------"
# 方法1：使用ip命令
if command -v ip >/dev/null 2>&1; then
    ip addr show | grep -E "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1
else
    # 方法2：使用ifconfig命令
    ifconfig | grep -E "inet " | grep -v "127.0.0.1" | awk '{print $2}'
fi
echo ""

# 3. 查看主机名
echo "3. 主机名："
echo "----------------------------------------"
hostname
echo ""

# 4. 查看域名（如果有）
echo "4. 域名信息："
echo "----------------------------------------"
if [ -n "$(hostname -f 2>/dev/null)" ]; then
    hostname -f
else
    echo "未配置域名"
fi
echo ""

# 5. 查看SSH连接信息
echo "5. SSH连接信息："
echo "----------------------------------------"
echo "当前SSH连接："
who am i 2>/dev/null || echo "无法获取SSH连接信息"
echo ""

echo "=========================================="
echo "使用说明"
echo "=========================================="
echo ""
echo "从Windows上传字体文件到服务器："
echo ""
echo "方法1：使用公网IP"
echo "  scp C:\\Windows\\Fonts\\simsun.ttc admin@$PUBLIC_IP:/tmp/"
echo ""
echo "方法2：使用内网IP（如果在同一内网）"
echo "  scp C:\\Windows\\Fonts\\simsun.ttc admin@<内网IP>:/tmp/"
echo ""
echo "方法3：使用域名（如果有）"
echo "  scp C:\\Windows\\Fonts\\simsun.ttc admin@www.geshixiugai.cn:/tmp/"
echo ""
echo "注意："
echo "1. 确保服务器的SSH端口（通常是22）已开放"
echo "2. 如果使用公网IP，确保安全组规则允许SSH连接"
echo "3. 首次连接可能需要确认服务器指纹"
echo ""

