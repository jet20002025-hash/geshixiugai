# 安装 WeasyPrint - 完整步骤

## 🔍 问题：WeasyPrint 未安装

虽然日志显示 "WeasyPrint导入成功"，但可能是：
1. 虚拟环境没有激活
2. 或者在不同的 Python 环境中运行

## 🚀 完整安装步骤

### 步骤1: 确保在虚拟环境中

```bash
cd /var/www/geshixiugai

# 激活虚拟环境
source venv/bin/activate

# 确认虚拟环境已激活（应该显示 (venv)）
which python
```

### 步骤2: 安装系统依赖（重要！）

```bash
# CentOS/RHEL/Alibaba Cloud Linux
sudo yum install -y \
    cairo-devel \
    pango-devel \
    gdk-pixbuf2-devel \
    libffi-devel \
    python3-devel
```

### 步骤3: 安装 WeasyPrint 和 pypdf

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 安装兼容版本组合
pip install weasyprint==60.2 pypdf==3.15.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者使用 requirements.txt 中的版本
pip install weasyprint==62.3 pypdf==3.16.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤4: 验证安装

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 检查 WeasyPrint
python -c "import weasyprint; print('WeasyPrint版本:', weasyprint.__version__)"

# 检查 pypdf
python -c "import pypdf; print('pypdf版本:', pypdf.__version__)"

# 测试导入
python -c "from weasyprint import HTML; print('✅ WeasyPrint导入成功')"
```

### 步骤5: 更新 requirements.txt

```bash
# 如果使用新版本，更新 requirements.txt
pip freeze | grep -E "weasyprint|pypdf"
```

### 步骤6: 重启服务

```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

## ⚠️ 如果安装失败

### 问题1: 缺少系统依赖

```bash
# 安装所有必要的系统依赖
sudo yum install -y \
    cairo-devel \
    pango-devel \
    gdk-pixbuf2-devel \
    libffi-devel \
    python3-devel \
    gcc \
    python3-pip
```

### 问题2: 编译错误

```bash
# 尝试使用预编译的 wheel
pip install --only-binary :all: weasyprint -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3: 网络问题

```bash
# 使用国内镜像，增加超时时间
pip install --default-timeout=100 weasyprint==60.2 pypdf==3.15.0 \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📋 推荐版本组合

为了避免 transform 错误，推荐使用：

```bash
pip install weasyprint==60.2 pypdf==3.15.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

这个组合更稳定，不容易出现 transform 错误。




