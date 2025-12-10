# 测试 WeasyPrint PDF 生成

## ✅ LibreOffice 已卸载

现在系统将使用 WeasyPrint 生成 PDF。

## 🚀 更新代码并测试

### 步骤1: 更新代码

```bash
cd /var/www/geshixiugai
git pull origin main
```

### 步骤2: 重启服务

```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

### 步骤3: 查看日志

```bash
# 实时监控 PDF 生成日志
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```

## 📊 预期日志输出

成功时应该看到：

```
[PDF预览] 开始生成PDF预览，输入文件: ...
[PDF预览] WeasyPrint导入成功
[PDF预览] 开始生成HTML预览: ...
[PDF预览] 提取页面设置: A4, 方向: portrait, 页边距: ...
[PDF预览] 开始转换HTML到PDF，HTML大小: ... KB
[PDF预览] HTML中包含 ... 个img标签，其中 ... 个使用data URI
[PDF预览] 开始生成PDF文件...
[PDF预览] PDF生成成功，大小: ... KB
```

## ⚠️ 如果仍然出现 transform 错误

如果仍然出现 `'super' object has no attribute 'transform'` 错误，可能需要：

1. **降级 WeasyPrint**：
```bash
source venv/bin/activate
pip install weasyprint==60.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. **降级 pypdf**：
```bash
pip install pypdf==3.16.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. **或者完全移除 watermark**（如果不需要水印）

## 🐛 故障排查

如果 PDF 生成失败，检查：

1. **WeasyPrint 是否安装**：
```bash
source venv/bin/activate
python -c "from weasyprint import HTML; print('WeasyPrint导入成功')"
```

2. **查看详细错误日志**：
```bash
sudo journalctl -u geshixiugai -n 100 | grep -A 10 "\[PDF预览\]"
```

3. **检查依赖**：
```bash
source venv/bin/activate
pip list | grep -E "weasyprint|pypdf"
```


