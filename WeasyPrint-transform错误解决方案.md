# WeasyPrint 'super' object has no attribute 'transform' 错误解决方案

## 问题描述

PDF生成时出现错误：`'super' object has no attribute 'transform'`

这是 WeasyPrint 与 pypdf 版本不兼容导致的。

## 解决方案

### 方案1：降级 pypdf（推荐）

```bash
cd /var/www/geshixiugai
source venv/bin/activate
pip install pypdf==3.16.0
```

### 方案2：更新 WeasyPrint

```bash
cd /var/www/geshixiugai
source venv/bin/activate
pip install --upgrade weasyprint
```

### 方案3：同时更新和降级

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 先卸载
pip uninstall weasyprint pypdf -y

# 安装兼容版本
pip install weasyprint==62.3 pypdf==3.16.0
```

### 方案4：使用 requirements.txt 重新安装

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 修改 requirements.txt，将 pypdf 改为 3.16.0
# 然后重新安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 验证

安装后测试：

```bash
python -c "from weasyprint import HTML; print('WeasyPrint导入成功')"
```

## 如果还是不行

可能需要检查系统依赖：

```bash
# 检查 WeasyPrint 依赖
python -c "import weasyprint; print(weasyprint.__version__)"
python -c "import pypdf; print(pypdf.__version__)"
```




