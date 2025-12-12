#!/bin/bash

# 诊断文件内容问题的脚本

echo "=========================================="
echo "诊断文件内容问题"
echo "=========================================="
echo ""

# 1. 检查最近的转换日志
echo "1. 检查最近的转换日志..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 100 --no-pager | grep -E "Word转PDF|文件保存|文件大小|文件前20字节" | tail -n 30
echo ""

# 2. 检查错误日志
echo "2. 检查错误日志..."
echo "----------------------------------------"
tail -n 100 /var/log/geshixiugai/error.log | grep -E "Word转PDF|文件保存|文件大小|文件前20字节" | tail -n 30
echo ""

# 3. 检查临时文件（如果存在）
echo "3. 检查临时文件..."
echo "----------------------------------------"
TEMP_DIRS=$(find /tmp -maxdepth 1 -type d -name "word_to_pdf_*" 2>/dev/null | head -n 5)
if [ -n "$TEMP_DIRS" ]; then
    for dir in $TEMP_DIRS; do
        echo "临时目录: $dir"
        ls -lh "$dir" 2>/dev/null | head -n 10
        echo ""
    done
else
    echo "未找到临时目录（可能已被清理）"
fi
echo ""

# 4. 检查 LibreOffice 转换日志
echo "4. 检查 LibreOffice 转换日志..."
echo "----------------------------------------"
sudo journalctl -u geshixiugai -n 200 --no-pager | grep -E "PDF预览|LibreOffice|转换" | tail -n 30
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "请检查："
echo "1. 文件保存大小是否与上传大小一致"
echo "2. 文件前20字节是否正确（DOCX应该是PK开头）"
echo "3. LibreOffice转换是否成功"
echo "4. PDF文件头是否正确（应该是%PDF-开头）"
echo ""



