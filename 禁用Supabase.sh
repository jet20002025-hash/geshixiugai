#!/bin/bash

# 禁用 Supabase 存储配置

echo "=========================================="
echo "禁用 Supabase 存储"
echo "=========================================="
echo ""

ENV_FILE="/var/www/geshixiugai/.env"

# 检查 .env 文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env 文件不存在: $ENV_FILE"
    exit 1
fi

# 备份原文件
BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "1. 备份原配置文件..."
sudo cp "$ENV_FILE" "$BACKUP_FILE"
echo "✅ 已备份到: $BACKUP_FILE"
echo ""

# 禁用 Supabase 配置（注释掉或设置为空）
echo "2. 禁用 Supabase 配置..."
sudo sed -i 's/^SUPABASE_URL=.*/#SUPABASE_URL=/' "$ENV_FILE"
sudo sed -i 's/^SUPABASE_KEY=.*/#SUPABASE_KEY=/' "$ENV_FILE"
sudo sed -i 's/^SUPABASE_BUCKET=.*/#SUPABASE_BUCKET=/' "$ENV_FILE"

# 确保设置为空值（如果注释不起作用）
if ! grep -q "^#SUPABASE_URL=" "$ENV_FILE"; then
    echo "SUPABASE_URL=" | sudo tee -a "$ENV_FILE" > /dev/null
fi
if ! grep -q "^#SUPABASE_KEY=" "$ENV_FILE"; then
    echo "SUPABASE_KEY=" | sudo tee -a "$ENV_FILE" > /dev/null
fi
if ! grep -q "^#SUPABASE_BUCKET=" "$ENV_FILE"; then
    echo "SUPABASE_BUCKET=" | sudo tee -a "$ENV_FILE" > /dev/null
fi

echo "✅ 已禁用 Supabase 配置"
echo ""

# 显示修改后的配置
echo "3. 验证配置..."
echo "----------------------------------------"
grep -E "^#?SUPABASE" "$ENV_FILE" || echo "未找到 SUPABASE 配置"
echo ""

# 重启服务
echo "4. 重启服务以应用更改..."
echo "----------------------------------------"
sudo systemctl restart geshixiugai

# 等待服务启动
sleep 3

# 检查服务状态
if sudo systemctl is-active --quiet geshixiugai; then
    echo "✅ 服务已成功重启"
else
    echo "⚠️ 服务可能未正常启动，请检查日志："
    echo "   sudo journalctl -u geshixiugai -n 50"
fi

echo ""
echo "=========================================="
echo "完成"
echo "=========================================="
echo ""
echo "现在系统将使用本地文件系统存储，文件保存在："
echo "  /var/www/geshixiugai/storage/"
echo ""
echo "如果需要恢复 Supabase 配置，可以从备份文件恢复："
echo "  sudo cp $BACKUP_FILE $ENV_FILE"
echo ""

