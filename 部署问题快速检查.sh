#!/bin/bash

# 部署问题快速检查脚本

echo "🔍 开始检查部署问题..."

# 1. 检查 Python 语法
echo ""
echo "1. 检查 Python 语法..."
python3 -m py_compile backend/app/services/document_service.py 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 语法检查通过"
else
    echo "❌ 语法检查失败"
    exit 1
fi

# 2. 检查导入
echo ""
echo "2. 检查模块导入..."
python3 -c "
import sys
sys.path.insert(0, 'backend')
try:
    from app.services.document_service import DocumentService
    print('✅ DocumentService 导入成功')
except Exception as e:
    print(f'❌ DocumentService 导入失败: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
" 2>&1

# 3. 检查应用创建
echo ""
echo "3. 检查应用创建..."
python3 -c "
import sys
sys.path.insert(0, 'backend')
try:
    from app.main import create_app
    app = create_app()
    print('✅ 应用创建成功')
except Exception as e:
    print(f'❌ 应用创建失败: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
" 2>&1

# 4. 检查依赖
echo ""
echo "4. 检查依赖文件..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 存在"
    echo "依赖列表："
    cat requirements.txt
else
    echo "❌ requirements.txt 不存在"
    exit 1
fi

# 5. 检查 Vercel 配置
echo ""
echo "5. 检查 Vercel 配置..."
if [ -f "vercel.json" ]; then
    echo "✅ vercel.json 存在"
    cat vercel.json
else
    echo "⚠️ vercel.json 不存在"
fi

# 6. 检查 API 入口
echo ""
echo "6. 检查 API 入口..."
if [ -f "api/index.py" ]; then
    echo "✅ api/index.py 存在"
    python3 -m py_compile api/index.py 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ API 入口语法正确"
    else
        echo "❌ API 入口语法错误"
        exit 1
    fi
else
    echo "❌ api/index.py 不存在"
    exit 1
fi

echo ""
echo "✅ 所有检查完成！"

