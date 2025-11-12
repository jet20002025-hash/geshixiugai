#!/bin/bash

# Vercel 快速部署脚本

echo "🚀 开始部署到 Vercel..."

# 检查是否安装了 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ 未安装 Vercel CLI"
    echo "请运行: npm i -g vercel"
    exit 1
fi

# 检查是否登录
if ! vercel whoami &> /dev/null; then
    echo "🔐 请先登录 Vercel..."
    vercel login
fi

# 部署
echo "📦 正在部署..."
vercel --prod

echo "✅ 部署完成！"
echo "📝 请记得在 Vercel 项目设置中配置环境变量："
echo "   - R2_ACCOUNT_ID"
echo "   - R2_ACCESS_KEY_ID"
echo "   - R2_SECRET_ACCESS_KEY"
echo "   - R2_BUCKET_NAME"
echo "   - R2_ENDPOINT"

