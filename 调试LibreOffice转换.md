# 调试 LibreOffice PDF 转换

## 🔍 问题分析

LibreOffice 命令执行了，但是没有生成 PDF 文件。可能的原因：

1. **转换失败但没有返回错误码**
2. **权限问题**：运行服务的用户没有写入权限
3. **路径问题**：相对路径或绝对路径问题
4. **LibreOffice 配置问题**：需要额外的参数或配置

## 🧪 手动测试

在服务器上手动测试 LibreOffice 转换：

```bash
# 1. 切换到文档目录
cd /var/www/geshixiugai/storage/documents

# 2. 创建一个测试目录
mkdir -p test_libreoffice
cd test_libreoffice

# 3. 复制一个预览文档
cp ../*/preview.docx test.docx

# 4. 手动执行 LibreOffice 转换
libreoffice --headless --convert-to pdf --outdir . test.docx

# 5. 检查是否生成 PDF
ls -lh *.pdf

# 6. 检查返回码和输出
echo $?
```

## 🔧 检查权限

```bash
# 检查运行服务的用户
ps aux | grep gunicorn | head -1

# 检查文档目录权限
ls -ld /var/www/geshixiugai/storage/documents

# 检查是否有写入权限
touch /var/www/geshixiugai/storage/documents/test_write.txt
rm /var/www/geshixiugai/storage/documents/test_write.txt
```

## 📋 查看详细日志

更新代码后，重新上传文档，查看详细日志：

```bash
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```

应该能看到：
- LibreOffice 的返回码
- 标准输出
- 错误输出
- 等待文件生成的日志

## 💡 可能的解决方案

### 方案1: 使用不同的输出方式

LibreOffice 可能需要在当前目录输出，而不是指定 `--outdir`：

```bash
# 先切换到输出目录，然后执行
cd /path/to/output
libreoffice --headless --convert-to pdf input.docx
```

### 方案2: 添加更多参数

```bash
libreoffice --headless --invisible --nodefault --nolockcheck \
  --convert-to pdf --outdir /path/to/output input.docx
```

### 方案3: 检查 LibreOffice 版本

某些版本的 LibreOffice 可能有 bug：

```bash
libreoffice --version
```

## 🐛 如果仍然失败

如果手动测试成功，但代码中失败，可能是：
1. **环境变量问题**：PATH、HOME 等
2. **用户权限问题**：运行服务的用户权限不足
3. **工作目录问题**：需要在正确的目录执行

请提供手动测试的结果，我会根据实际情况调整代码。


