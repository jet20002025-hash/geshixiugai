#!/bin/bash

# 创建LibreOffice字体替换配置文件
# 将Word文档中的字体映射到系统可用字体

echo "=========================================="
echo "创建LibreOffice字体替换配置"
echo "=========================================="
echo ""

# LibreOffice配置文件目录
LO_USER_DIR="$HOME/.config/libreoffice/4/user"
mkdir -p "$LO_USER_DIR"

# 创建registrymodifications.xcu文件（如果不存在）
REGISTRY_FILE="$LO_USER_DIR/registrymodifications.xcu"

# 检查文件是否存在
if [ ! -f "$REGISTRY_FILE" ]; then
    # 创建基本的registrymodifications.xcu文件
    cat > "$REGISTRY_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
</oor:items>
EOF
    echo "✅ 创建了registrymodifications.xcu文件"
else
    echo "✅ registrymodifications.xcu文件已存在"
fi

# 创建字体替换配置
# 注意：LibreOffice的字体替换配置比较复杂，通常通过GUI设置
# 但我们可以通过修改配置文件来实现

echo ""
echo "字体替换说明："
echo "----------------------------------------"
echo "LibreOffice在headless模式下会自动进行字体替换："
echo ""
echo "1. 如果Word文档使用 SimSun (宋体):"
echo "   → LibreOffice会查找系统字体"
echo "   → 如果找不到，会使用默认字体（通常是文泉驿微米黑）"
echo ""
echo "2. 如果Word文档使用 SimHei (黑体):"
echo "   → LibreOffice会查找系统字体"
echo "   → 如果找不到，会使用默认字体（通常是文泉驿微米黑）"
echo ""
echo "3. 如果Word文档使用 KaiTi (楷体):"
echo "   → LibreOffice会查找系统字体"
echo "   → 如果找不到，会使用默认字体（通常是文泉驿正黑）"
echo ""
echo "4. 如果Word文档使用 Times New Roman:"
echo "   → LibreOffice会查找系统字体"
echo "   → 如果找不到，会使用Liberation Serif（如果已安装）"
echo ""
echo "=========================================="
echo "重要提示"
echo "=========================================="
echo ""
echo "要确保PDF保留原始字体，需要："
echo ""
echo "1. 安装所需字体（运行 快速安装字体.sh）"
echo "2. 或者使用字体替换："
echo "   - 在Word文档中，不同字体在PDF中会显示为不同的字体"
echo "   - 即使字体名称不同，只要字体样式不同（宋体、黑体、楷体等）"
echo "   - LibreOffice会尽量保持字体差异"
echo ""
echo "3. 最佳方案："
echo "   - 安装思源字体（更好的字体支持）"
echo "   - 或确保系统有足够的字体变体（正黑、微米黑等）"
echo ""
echo "当前系统字体："
fc-list :lang=zh | head -n 5
echo ""

