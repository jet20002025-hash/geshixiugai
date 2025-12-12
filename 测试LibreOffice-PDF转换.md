# 测试 LibreOffice PDF 转换

## ✅ 确认 LibreOffice 已安装

```bash
which libreoffice
# 输出: /usr/bin/libreoffice

libreoffice --version
# 输出: LibreOffice 7.1.8.1 10(Build:1)
```

## 🚀 更新代码并重启

```bash
# 1. 更新代码
cd /var/www/geshixiugai
git pull origin main

# 2. 重启服务
sudo systemctl restart geshixiugai

# 3. 检查服务状态
sudo systemctl status geshixiugai
```

## 📊 查看日志

```bash
# 实时监控 PDF 生成日志
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```

## ✅ 预期日志输出

成功时应该看到：

```
[PDF预览] 开始生成PDF预览，输入文件: ...
[PDF预览] 找到LibreOffice命令: /usr/bin/libreoffice
[PDF预览] 执行LibreOffice PDF转换命令: libreoffice --headless --convert-to pdf ...
[PDF预览] LibreOffice PDF转换成功，大小: XXX KB
[PDF预览] ✅ 使用LibreOffice转换PDF成功（最接近Word效果）
```

## ⚠️ 如果仍然检测不到

如果更新后仍然显示 "LibreOffice未找到"，请检查：

1. **服务用户权限**：确保运行服务的用户（如 `nginx` 或 `admin`）可以访问 `/usr/bin/libreoffice`

```bash
# 检查服务运行用户
ps aux | grep gunicorn

# 检查权限
ls -l /usr/bin/libreoffice

# 如果权限不足，可以创建符号链接或调整权限
sudo chmod +x /usr/bin/libreoffice
```

2. **PATH 环境变量**：确保服务的 PATH 包含 `/usr/bin`

```bash
# 检查 gunicorn 服务的环境变量
sudo systemctl show geshixiugai | grep Environment
```

3. **手动测试转换**：验证 LibreOffice 是否能正常转换

```bash
# 创建一个测试文档
cd /tmp
echo "测试" > test.txt

# 测试转换
libreoffice --headless --convert-to pdf test.txt

# 检查是否生成 PDF
ls -lh test.pdf
```

## 🔧 如果检测逻辑仍然失败

可以手动指定 LibreOffice 路径（需要修改代码）：

在 `document_service.py` 中，可以硬编码路径：

```python
libreoffice_cmd = '/usr/bin/libreoffice'
```

但更好的方法是使用环境变量：

```bash
# 在 .env 文件中添加
LIBREOFFICE_CMD=/usr/bin/libreoffice
```

然后在代码中读取环境变量。




