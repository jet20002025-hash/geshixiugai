#!/bin/bash

# 自动提交并推送到 GitHub 的脚本
# 使用方法: ./提交并推送.sh "提交信息"

# 获取提交信息（如果提供了参数）
COMMIT_MSG="${1:-自动提交：代码更新}"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "开始提交并推送到 GitHub"
echo "=========================================="
echo ""

# 1. 检查是否有未提交的更改
echo -e "${YELLOW}1. 检查更改...${NC}"
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ 没有未提交的更改${NC}"
    exit 0
fi

# 显示更改的文件
echo "更改的文件："
git status --short
echo ""

# 2. 添加所有更改
echo -e "${YELLOW}2. 添加更改到暂存区...${NC}"
git add -A
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 文件已添加到暂存区${NC}"
else
    echo -e "${RED}❌ 添加文件失败${NC}"
    exit 1
fi
echo ""

# 3. 提交更改
echo -e "${YELLOW}3. 提交更改...${NC}"
echo "提交信息: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 提交成功${NC}"
else
    echo -e "${RED}❌ 提交失败${NC}"
    exit 1
fi
echo ""

# 4. 推送到 GitHub
echo -e "${YELLOW}4. 推送到 GitHub...${NC}"
git push origin main
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 推送成功${NC}"
else
    echo -e "${RED}❌ 推送失败${NC}"
    exit 1
fi
echo ""

# 5. 显示最新提交
echo -e "${YELLOW}5. 最新提交信息：${NC}"
git log --oneline -1
echo ""

echo "=========================================="
echo -e "${GREEN}✅ 完成！代码已推送到 GitHub${NC}"
echo "=========================================="

