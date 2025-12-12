# 修复 LibreOffice 权限问题

## 🔍 问题分析

文件属于 `nginx` 用户，但当前以 `admin` 用户运行 LibreOffice，可能导致权限问题。

## ✅ 解决方案

### 方案1: 以 nginx 用户身份运行（推荐）

```bash
# 以 nginx 用户身份执行转换
sudo -u nginx libreoffice --headless --convert-to pdf \
  --outdir /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 检查结果
ls -lh /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.pdf
```

### 方案2: 临时修改文件权限（测试用）

```bash
# 临时添加读取权限（仅用于测试）
sudo chmod o+r /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 执行转换
libreoffice --headless --convert-to pdf \
  --outdir /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx

# 恢复权限（测试后）
sudo chmod o-r /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx
```

### 方案3: 复制到临时目录（最简单）

```bash
# 复制到临时目录（admin用户可以访问）
sudo cp /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx /tmp/test.docx

# 转换
cd /tmp
libreoffice --headless --convert-to pdf test.docx

# 检查结果
ls -lh test.pdf

# 如果成功，复制回原目录
sudo cp /tmp/test.pdf /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.pdf
sudo chown nginx:nginx /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.pdf
```

## 🔧 修改代码以使用正确的用户

如果方案1成功，需要修改代码，确保 LibreOffice 以正确的用户身份运行。

代码中应该使用 `sudo -u nginx` 或者确保运行服务的用户有权限访问文件。

## 📋 测试步骤

1. **先测试方案1**（以nginx用户运行）：
```bash
sudo -u nginx libreoffice --headless --convert-to pdf \
  --outdir /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc \
  /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.docx
```

2. **如果成功，检查PDF**：
```bash
ls -lh /var/www/geshixiugai/storage/documents/01a4656f3b5046bb9c45a53d322034bc/preview.pdf
```

3. **如果失败，尝试方案3**（复制到临时目录）

## ⚠️ 注意事项

- 服务运行时，gunicorn 进程可能以 `nginx` 用户运行
- 需要确保 LibreOffice 命令可以以该用户身份执行
- 可能需要配置 sudo 规则，允许 nginx 用户执行 libreoffice




