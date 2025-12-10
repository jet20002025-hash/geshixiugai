# WeasyPrint 'super' object has no attribute 'transform' 完整解决方案

## 问题原因

这个错误不是 WeasyPrint 核心代码的问题，而是与底层图形库（cairo/pango）的版本不兼容或缺失有关。

## 完整解决步骤

### 步骤1：检查并安装系统依赖（重要！）

```bash
# 对于 CentOS/RHEL/Alibaba Cloud Linux
sudo yum install -y \
    cairo-devel \
    pango-devel \
    gdk-pixbuf2-devel \
    libffi-devel \
    python3-devel

# 或者对于较新的系统
sudo dnf install -y \
    cairo-devel \
    pango-devel \
    gdk-pixbuf2-devel \
    libffi-devel \
    python3-devel
```

### 步骤2：更新代码和依赖

```bash
cd /var/www/geshixiugai

# 更新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 重新安装 WeasyPrint 和相关依赖
pip uninstall weasyprint pypdf -y
pip install weasyprint==62.3 pypdf==3.16.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者安装最新版本
# pip install --upgrade weasyprint -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤3：验证安装

```bash
# 检查 WeasyPrint 是否能正常导入
python -c "from weasyprint import HTML; print('✅ WeasyPrint导入成功')"

# 检查版本
python -c "import weasyprint; print('WeasyPrint版本:', weasyprint.__version__)"
python -c "import pypdf; print('pypdf版本:', pypdf.__version__)"
```

### 步骤4：测试 PDF 生成

```bash
# 创建一个简单的测试
python << 'EOF'
from weasyprint import HTML
html_content = '<html><body><h1>Test</h1></body></html>'
HTML(string=html_content).write_pdf('/tmp/test.pdf')
print('✅ PDF生成测试成功')
EOF
```

### 步骤5：重启服务

```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

## 如果还是不行

### 方案A：降级 WeasyPrint

```bash
pip uninstall weasyprint -y
pip install weasyprint==60.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方案B：检查系统库版本

```bash
# 检查 cairo 版本
pkg-config --modversion cairo

# 检查 pango 版本
pkg-config --modversion pango
```

### 方案C：使用替代方案

如果 WeasyPrint 一直有问题，可以考虑：
1. 使用 LibreOffice 转换（之前讨论过）
2. 使用其他 PDF 生成库（如 reportlab）

## 快速修复命令（一键执行）

```bash
cd /var/www/geshixiugai && \
sudo yum install -y cairo-devel pango-devel gdk-pixbuf2-devel libffi-devel python3-devel && \
source venv/bin/activate && \
pip uninstall weasyprint pypdf -y && \
pip install weasyprint==62.3 pypdf==3.16.0 -i https://pypi.tuna.tsinghua.edu.cn/simple && \
python -c "from weasyprint import HTML; print('✅ WeasyPrint导入成功')" && \
sudo systemctl restart geshixiugai
```

