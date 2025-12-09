# WeasyPrint 安装完成后的操作

## ✅ 安装完成！

现在需要更新代码并重启服务，让 PDF 预览功能生效。

---

## 🚀 下一步操作

### 步骤 1：更新代码（如果还没更新）

在阿里云服务器的远程连接终端里执行：

```bash
# 进入项目目录
cd /var/www/geshixiugai

# 从 GitHub 拉取最新代码
git pull origin main
```

**如果提示有冲突或需要输入密码：**
- 检查是否有未提交的更改
- 或者先备份，然后强制拉取（谨慎使用）

---

### 步骤 2：重启服务

```bash
# 重启服务
sudo systemctl restart geshixiugai

# 检查服务状态
sudo systemctl status geshixiugai
```

**应该看到：**
```
Active: active (running)
```

---

### 步骤 3：验证 PDF 预览功能

1. **重新处理一个文档**
   - 访问你的网站
   - 上传一个文档并处理

2. **查看日志，确认 PDF 生成**
   ```bash
   # 查看服务日志
   sudo journalctl -u geshixiugai -f
   ```

   应该看到类似这样的日志：
   ```
   [PDF预览] 开始转换HTML到PDF，HTML大小: 123.45 KB
   [PDF预览] PDF生成成功，大小: 234.56 KB
   ```

3. **测试预览功能**
   - 点击"预览文档"按钮
   - 应该显示 PDF 格式的预览
   - 浏览器会直接显示 PDF（不需要下载）

---

## 🔍 如何确认 PDF 预览正常工作

### 方法 1：查看日志

```bash
# 实时查看日志
sudo journalctl -u geshixiugai -f

# 处理一个文档后，应该看到：
# [PDF预览] PDF生成成功，大小: XXX KB
```

### 方法 2：检查文件

```bash
# 进入项目目录
cd /var/www/geshixiugai

# 查看 storage 目录（如果有本地存储）
find storage -name "*.pdf" -type f | head -5

# 或者查看文档目录
ls -lh storage/documents/*/preview.pdf 2>/dev/null | head -5
```

### 方法 3：直接测试

1. 访问网站
2. 上传并处理一个文档
3. 点击"预览文档"
4. 如果显示 PDF（而不是 HTML），说明成功！

---

## ⚠️ 如果 PDF 预览不工作

### 检查 1：WeasyPrint 是否真的安装成功

```bash
python -c "import weasyprint; print('版本:', weasyprint.__version__)"
```

如果报错，说明安装有问题。

### 检查 2：查看错误日志

```bash
# 查看最近的错误日志
sudo journalctl -u geshixiugai -n 100 | grep -i "pdf\|weasyprint\|error"
```

### 检查 3：检查代码是否更新

```bash
cd /var/www/geshixiugai
git log --oneline -5
```

应该看到包含 "PDF预览" 或 "weasyprint" 的提交。

---

## 📋 完整操作清单

在阿里云服务器的远程连接终端里，依次执行：

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 更新代码
git pull origin main

# 3. 验证 WeasyPrint 安装
python -c "import weasyprint; print('✅ WeasyPrint 版本:', weasyprint.__version__)"

# 4. 重启服务
sudo systemctl restart geshixiugai

# 5. 检查服务状态
sudo systemctl status geshixiugai

# 6. 查看日志（可选，用于监控）
sudo journalctl -u geshixiugai -f
```

---

## 🎉 完成！

现在你的系统应该支持 PDF 预览了！

**优势：**
- ✅ 预览格式完美保留（与 Word 文档一致）
- ✅ 浏览器原生支持（无需插件）
- ✅ 无需安装 LibreOffice
- ✅ 文件大小更小

---

## 💡 小贴士

1. **如果 PDF 生成失败**：系统会自动回退到 HTML 预览
2. **查看日志**：遇到问题可以查看日志排查
3. **性能**：PDF 生成可能需要几秒钟，大文档会更慢

---

**现在去测试一下 PDF 预览功能吧！** 🚀

