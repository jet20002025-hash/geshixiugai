#!/bin/bash

# 服务器端解决 git pull 冲突的脚本

cd /var/www/geshixiugai

echo "=========================================="
echo "解决 git pull 冲突"
echo "=========================================="
echo ""

# 1. 检查本地更改
echo "1. 检查本地更改..."
git status --short
echo ""

# 2. 选择处理方式
echo "2. 处理本地更改..."
echo "   选项1: 暂存本地更改（推荐，保留本地修改）"
echo "   选项2: 提交本地更改"
echo "   选项3: 丢弃本地更改（如果不需要保留）"
echo ""

# 使用暂存方式（推荐）
echo "使用暂存方式处理..."
git stash
if [ $? -eq 0 ]; then
    echo "   ✅ 本地更改已暂存"
else
    echo "   ⚠️  暂存失败，尝试其他方式"
fi
echo ""

# 3. 拉取最新代码
echo "3. 拉取最新代码..."
git pull origin main
if [ $? -eq 0 ]; then
    echo "   ✅ 代码已更新"
else
    echo "   ❌ 拉取失败"
    exit 1
fi
echo ""

# 4. 如果需要恢复本地更改
echo "4. 如果需要恢复本地更改，执行:"
echo "   git stash pop"
echo ""

echo "=========================================="
echo "完成！"
echo "=========================================="

