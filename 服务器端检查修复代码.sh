#!/bin/bash

# 检查服务器端修复代码是否已更新

cd /var/www/geshixiugai

echo "=========================================="
echo "检查修复代码是否已更新"
echo "=========================================="
echo ""

# 1. 检查是否包含修复前检测
echo "1. 检查是否包含修复前检测代码..."
if grep -q "修复前检测" backend/app/services/document_service.py; then
    echo "   ✅ 找到修复前检测代码"
    grep -n "修复前检测" backend/app/services/document_service.py | head -3
else
    echo "   ❌ 未找到修复前检测代码"
fi
echo ""

# 2. 检查是否包含修复后检测
echo "2. 检查是否包含修复后检测代码..."
if grep -q "修复后检测" backend/app/services/document_service.py; then
    echo "   ✅ 找到修复后检测代码"
    grep -n "修复后检测" backend/app/services/document_service.py | head -3
else
    echo "   ❌ 未找到修复后检测代码"
fi
echo ""

# 3. 检查是否包含开始修复
echo "3. 检查是否包含开始修复代码..."
if grep -q "开始修复" backend/app/services/document_service.py; then
    echo "   ✅ 找到开始修复代码"
    grep -n "开始修复" backend/app/services/document_service.py | head -3
else
    echo "   ❌ 未找到开始修复代码"
fi
echo ""

# 4. 检查_log_to_file方法
echo "4. 检查_log_to_file方法..."
if grep -q "_log_to_file" backend/app/services/document_service.py; then
    COUNT=$(grep -c "_log_to_file" backend/app/services/document_service.py)
    echo "   ✅ 找到 _log_to_file 方法，使用次数: $COUNT"
else
    echo "   ❌ 未找到 _log_to_file 方法"
fi
echo ""

# 5. 检查修复函数
echo "5. 检查修复函数..."
if grep -q "_ensure_integrity_abstract_separation" backend/app/services/document_service.py; then
    echo "   ✅ 找到修复函数"
    grep -n "def _ensure_integrity_abstract_separation" backend/app/services/document_service.py
else
    echo "   ❌ 未找到修复函数"
fi
echo ""

# 6. 查看修复函数的调用
echo "6. 查看修复函数的调用位置..."
grep -n "_ensure_integrity_abstract_separation" backend/app/services/document_service.py | head -5
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="

