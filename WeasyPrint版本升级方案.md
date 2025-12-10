# WeasyPrint 版本升级方案

## 🔍 当前版本问题

- **WeasyPrint 62.3 + pypdf 3.16.0**: 出现 `transform` 错误
- **WeasyPrint 60.2 + pypdf 3.15.0**: 出现 `PDF.__init__()` 错误

## 🚀 可以尝试的版本组合

### 方案1: WeasyPrint 61.x + pypdf 3.12.0（推荐）

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 安装 WeasyPrint 61.2 和 pypdf 3.12.0
pip install weasyprint==61.2 pypdf==3.12.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方案2: WeasyPrint 62.3 + pypdf 3.10.0

```bash
# 使用最新 WeasyPrint，但降级 pypdf
pip install weasyprint==62.3 pypdf==3.10.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方案3: WeasyPrint 61.1 + pypdf 3.11.0

```bash
pip install weasyprint==61.1 pypdf==3.11.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📋 测试步骤

```bash
# 1. 安装新版本组合
pip install weasyprint==61.2 pypdf==3.12.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 验证版本
python -c "import weasyprint; print('WeasyPrint版本:', weasyprint.__version__)"
python -c "import pypdf; print('pypdf版本:', pypdf.__version__)"

# 3. 测试导入
python -c "from weasyprint import HTML; print('✅ WeasyPrint导入成功')"

# 4. 重启服务
sudo systemctl restart geshixiugai

# 5. 测试 PDF 生成
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```

## ⚠️ 注意事项

1. **版本兼容性**：不同版本的 WeasyPrint 需要不同版本的 pypdf
2. **功能差异**：新版本可能有新功能，但也可能有新 bug
3. **稳定性**：如果某个版本组合工作正常，建议固定使用

## 💡 推荐策略

1. **先尝试方案1**（WeasyPrint 61.2 + pypdf 3.12.0）
2. **如果失败，尝试方案2**（WeasyPrint 62.3 + pypdf 3.10.0）
3. **如果都失败，回退到 WeasyPrint 60.2 + pypdf 3.10.0**

## 🔄 如果所有版本都有问题

如果所有版本组合都有问题，可能需要：
1. 完全移除 watermark CSS
2. 或者使用其他 PDF 生成库（如 reportlab）
3. 或者等待 WeasyPrint 官方修复


