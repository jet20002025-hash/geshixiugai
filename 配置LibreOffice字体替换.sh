#!/bin/bash

# 配置LibreOffice字体替换规则
# 将常见的Windows字体映射到Linux可用字体

echo "=========================================="
echo "配置LibreOffice字体替换"
echo "=========================================="
echo ""

LO_CONFIG_DIR="$HOME/.config/libreoffice/4/user"
mkdir -p "$LO_CONFIG_DIR"

# 创建字体替换配置文件
FONT_REPLACE_FILE="$LO_CONFIG_DIR/fc-settings.xml"

cat > "$FONT_REPLACE_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<oor:component-data xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" oor:name="Common" oor:package="org.openoffice.Office">
  <node oor:name="Font">
    <node oor:name="FontSubstitution">
      <prop oor:name="FontSubst" oor:type="oor:string-list">
        <value>SimSun,文泉驿微米黑,文泉驿微米黑,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
        <value>SimHei,文泉驿微米黑,文泉驿微米黑,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
        <value>KaiTi,文泉驿正黑,文泉驿正黑,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
        <value>Microsoft YaHei,文泉驿微米黑,文泉驿微米黑,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
        <value>Times New Roman,Liberation Serif,Liberation Serif,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
        <value>宋体,文泉驿微米黑,文泉驿微米黑,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
        <value>黑体,文泉驿微米黑,文泉驿微米黑,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
        <value>楷体,文泉驿正黑,文泉驿正黑,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</value>
      </prop>
    </node>
  </node>
</node>
</oor:component-data>
EOF

echo "✅ 字体替换配置文件已创建: $FONT_REPLACE_FILE"
echo ""
echo "字体替换规则："
echo "  SimSun (宋体) -> 文泉驿微米黑"
echo "  SimHei (黑体) -> 文泉驿微米黑"
echo "  KaiTi (楷体) -> 文泉驿正黑"
echo "  Microsoft YaHei -> 文泉驿微米黑"
echo "  Times New Roman -> Liberation Serif"
echo ""
echo "注意："
echo "1. 此配置会在LibreOffice启动时自动加载"
echo "2. 如果安装了思源字体，可以修改替换规则使用思源字体"
echo "3. 需要重启LibreOffice或重启服务才能生效"
echo ""

