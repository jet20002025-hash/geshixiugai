#!/bin/bash

# 检查和修复 Supabase 配置

echo "=========================================="
echo "检查和修复 Supabase 配置"
echo "=========================================="
echo ""

ENV_FILE="/var/www/geshixiugai/.env"

# 检查 .env 文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env 文件不存在: $ENV_FILE"
    exit 1
fi

echo "1. 检查当前 Supabase 配置..."
echo "----------------------------------------"

# 检查 SUPABASE_URL
SUPABASE_URL=$(grep "^SUPABASE_URL=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [[ "$SUPABASE_URL" == *"你的项目ID"* ]] || [[ "$SUPABASE_URL" == *"your-project-id"* ]] || [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL 包含占位符或为空: $SUPABASE_URL"
    NEED_FIX=1
else
    echo "✅ SUPABASE_URL: $SUPABASE_URL"
fi

# 检查 SUPABASE_KEY
SUPABASE_KEY=$(grep "^SUPABASE_KEY=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [[ "$SUPABASE_KEY" == *"你的service_role"* ]] || [[ "$SUPABASE_KEY" == *"your-service-role"* ]] || [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY 包含占位符或为空"
    NEED_FIX=1
else
    # 检查是否包含非ASCII字符
    if ! echo "$SUPABASE_KEY" | grep -q '^[[:print:]]*$' || echo "$SUPABASE_KEY" | grep -q '[^[:ascii:]]'; then
        echo "⚠️ SUPABASE_KEY 可能包含非ASCII字符"
        NEED_FIX=1
    else
        KEY_PREVIEW="${SUPABASE_KEY:0:20}..."
        echo "✅ SUPABASE_KEY: $KEY_PREVIEW (长度: ${#SUPABASE_KEY})"
    fi
fi

# 检查 SUPABASE_BUCKET
SUPABASE_BUCKET=$(grep "^SUPABASE_BUCKET=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [ -z "$SUPABASE_BUCKET" ]; then
    echo "⚠️ SUPABASE_BUCKET 为空，将使用默认值"
else
    echo "✅ SUPABASE_BUCKET: $SUPABASE_BUCKET"
fi

echo ""
echo "=========================================="
echo "解决方案"
echo "=========================================="
echo ""

if [ "$NEED_FIX" = "1" ]; then
    echo "检测到配置问题，有两种解决方案："
    echo ""
    echo "方案1: 配置 Supabase（推荐，如果需要云存储）"
    echo "----------------------------------------"
    echo "1. 登录 Supabase 控制台: https://app.supabase.com"
    echo "2. 选择你的项目"
    echo "3. 进入 Settings > API"
    echo "4. 复制以下信息："
    echo "   - Project URL (格式: https://xxxxx.supabase.co)"
    echo "   - service_role key (在 Project API keys 中，选择 service_role)"
    echo ""
    echo "5. 编辑 .env 文件："
    echo "   sudo nano $ENV_FILE"
    echo ""
    echo "6. 替换以下行："
    echo "   SUPABASE_URL=https://你的实际项目ID.supabase.co"
    echo "   SUPABASE_KEY=你的实际service_role_key"
    echo ""
    echo "7. 保存后重启服务："
    echo "   sudo systemctl restart geshixiugai"
    echo ""
    echo "方案2: 禁用 Supabase 存储（使用本地文件系统）"
    echo "----------------------------------------"
    echo "如果不需要云存储，可以禁用 Supabase："
    echo ""
    echo "1. 编辑 .env 文件："
    echo "   sudo nano $ENV_FILE"
    echo ""
    echo "2. 注释掉或删除 Supabase 相关行，或设置为空："
    echo "   # SUPABASE_URL="
    echo "   # SUPABASE_KEY="
    echo "   # SUPABASE_BUCKET="
    echo ""
    echo "3. 或者设置 USE_STORAGE=false（如果存在此选项）"
    echo ""
    echo "4. 保存后重启服务："
    echo "   sudo systemctl restart geshixiugai"
    echo ""
    echo "=========================================="
    echo "快速禁用 Supabase（方案2）"
    echo "=========================================="
    read -p "是否现在禁用 Supabase 存储？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在禁用 Supabase 存储..."
        # 备份原文件
        sudo cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        
        # 注释掉 Supabase 配置
        sudo sed -i 's/^SUPABASE_URL=/#SUPABASE_URL=/' "$ENV_FILE"
        sudo sed -i 's/^SUPABASE_KEY=/#SUPABASE_KEY=/' "$ENV_FILE"
        sudo sed -i 's/^SUPABASE_BUCKET=/#SUPABASE_BUCKET=/' "$ENV_FILE"
        
        echo "✅ 已禁用 Supabase 配置"
        echo "✅ 已备份原文件到: ${ENV_FILE}.backup.*"
        echo ""
        echo "重启服务以应用更改："
        echo "  sudo systemctl restart geshixiugai"
    fi
else
    echo "✅ Supabase 配置看起来正确"
    echo ""
    echo "如果仍然遇到问题，请检查："
    echo "1. Supabase 项目是否已创建"
    echo "2. service_role key 是否有正确的权限"
    echo "3. Storage bucket 'word-formatter-storage' 是否已创建"
    echo "4. 服务是否已重启以加载新的环境变量"
fi

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="



