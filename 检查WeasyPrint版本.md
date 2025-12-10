# 检查 WeasyPrint 和相关库版本

## 📋 在服务器上执行以下命令

### 1. 检查 Python 包版本

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 检查 WeasyPrint 版本
python -c "import weasyprint; print('WeasyPrint版本:', weasyprint.__version__)"

# 检查 pypdf 版本
python -c "import pypdf; print('pypdf版本:', pypdf.__version__)"

# 检查 pycairo 版本（如果安装了）
python -c "import cairo; print('pycairo版本:', cairo.__version__)" 2>&1 || echo "pycairo未安装或无法导入"

# 检查所有相关包
pip list | grep -E "weasyprint|pypdf|cairo|pango"
```

### 2. 检查系统库版本

```bash
# 检查 cairo 系统库版本
pkg-config --modversion cairo 2>&1 || echo "cairo未安装"

# 检查 pango 系统库版本
pkg-config --modversion pango 2>&1 || echo "pango未安装"

# 检查所有相关系统库
rpm -qa | grep -E "cairo|pango"  # CentOS/RHEL
# 或
dpkg -l | grep -E "cairo|pango"  # Ubuntu/Debian
```

### 3. 查看 requirements.txt

```bash
cat /var/www/geshixiugai/requirements.txt | grep -E "weasyprint|pypdf"
```

## 🔍 当前 requirements.txt 中的版本

根据代码库，当前应该是：
- `weasyprint>=62.3` 或 `weasyprint==62.3`
- `pypdf<4.0.0` 或 `pypdf==3.16.0`

## 💡 如果版本不兼容

如果 WeasyPrint 62.3 与 pypdf 3.16.0 仍然不兼容，可以尝试：

1. **降级 WeasyPrint**：
```bash
pip install weasyprint==60.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. **降级 pypdf**：
```bash
pip install pypdf==3.15.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. **或者固定兼容版本组合**：
```bash
pip install weasyprint==60.2 pypdf==3.15.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```


