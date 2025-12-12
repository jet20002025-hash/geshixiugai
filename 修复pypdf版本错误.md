# 修复 pypdf 版本错误

## 🔍 错误：PDF.__init__() takes 1 positional argument but 3 were given

这是 pypdf 版本兼容性问题。WeasyPrint 60.2 需要特定版本的 pypdf。

## 🚀 解决方案

### 方案1: 降级 pypdf 到 3.10.0（推荐）

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 降级 pypdf
pip install pypdf==3.10.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证版本
python -c "import pypdf; print('pypdf版本:', pypdf.__version__)"
```

### 方案2: 尝试其他兼容版本

```bash
# 尝试 pypdf 3.9.0
pip install pypdf==3.9.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者 pypdf 3.8.0
pip install pypdf==3.8.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方案3: 升级 WeasyPrint（如果降级 pypdf 不行）

```bash
# 尝试 WeasyPrint 61.x 和 pypdf 3.12.0
pip install weasyprint==61.1 pypdf==3.12.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📋 推荐版本组合

根据错误信息，推荐尝试：

1. **WeasyPrint 60.2 + pypdf 3.10.0**（最稳定）
2. **WeasyPrint 60.2 + pypdf 3.9.0**（如果 3.10.0 不行）
3. **WeasyPrint 61.1 + pypdf 3.12.0**（如果前两个都不行）

## ✅ 测试步骤

```bash
# 1. 安装兼容版本
pip install pypdf==3.10.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 验证
python -c "import weasyprint; import pypdf; print('WeasyPrint:', weasyprint.__version__); print('pypdf:', pypdf.__version__)"

# 3. 重启服务
sudo systemctl restart geshixiugai

# 4. 测试 PDF 生成
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```




