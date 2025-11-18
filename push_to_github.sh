#!/bin/bash

# 推送代码到 GitHub 的脚本

cd "/Users/zwj/word格式修改器"

echo "=== 检查 Git 状态 ==="
git status

echo ""
echo "=== 添加所有更改 ==="
git add -A

echo ""
echo "=== 检查要提交的文件 ==="
git status --short

echo ""
echo "=== 提交更改 ==="
git commit -m "修复：将 python-alipay-sdk 版本从 3.7.0 降级到 3.4.0"

echo ""
echo "=== 设置远程仓库 ==="
git remote set-url origin https://github.com/jet20002025-hash/geshixiugai.git

echo ""
echo "=== 检查当前分支 ==="
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

echo ""
echo "=== 推送到 GitHub ==="
if [ "$CURRENT_BRANCH" = "main" ]; then
    git push -u origin main
elif [ "$CURRENT_BRANCH" = "master" ]; then
    git push -u origin master
else
    echo "尝试推送到 main 分支..."
    git push -u origin main 2>&1 || git push -u origin master 2>&1
fi

echo ""
echo "=== 完成 ==="
echo "如果推送成功，请检查 GitHub: https://github.com/jet20002025-hash/geshixiugai"

