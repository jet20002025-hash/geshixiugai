# LibreOffice PDF 转换方案（最接近 Word）

## 🎯 方案说明

由于 WeasyPrint 存在 `transform` 错误，现在**优先使用 LibreOffice 直接转换为 PDF**，这是最接近 Word 文档显示效果的方案。

## ✅ 优势

1. **完美保留格式**：字体、颜色、表格、图片等完全保留
2. **完美保留布局**：页边距、分页、页眉页脚与 Word 完全一致
3. **图片完美显示**：所有图片格式都支持（包括 WMF/EMF）
4. **无需额外依赖**：只需要安装 LibreOffice（系统级工具）

## 📦 安装 LibreOffice

### CentOS/RHEL/Alibaba Cloud Linux

```bash
sudo yum install -y libreoffice-headless
```

### Ubuntu/Debian

```bash
sudo apt install -y libreoffice --no-install-recommends
```

### 验证安装

```bash
libreoffice --version
# 或
soffice --version
```

## 🔄 工作流程

1. **优先尝试 LibreOffice 转 PDF**
   - 如果 LibreOffice 已安装，直接使用它转换
   - 转换命令：`libreoffice --headless --convert-to pdf --outdir <目录> <docx文件>`

2. **备用方案：WeasyPrint**
   - 如果 LibreOffice 未安装，回退到 WeasyPrint
   - 如果 WeasyPrint 也失败，会显示错误信息

## 🚀 部署步骤

在服务器上执行：

```bash
# 1. 安装 LibreOffice
sudo yum install -y libreoffice-headless

# 2. 更新代码
cd /var/www/geshixiugai
git pull origin main

# 3. 重启服务
sudo systemctl restart geshixiugai

# 4. 验证
libreoffice --version
```

## 📊 日志查看

转换时会看到以下日志：

```
[PDF预览] 开始生成PDF预览，输入文件: ...
[PDF预览] 执行LibreOffice PDF转换命令: libreoffice --headless --convert-to pdf ...
[PDF预览] LibreOffice PDF转换成功，大小: XXX KB
[PDF预览] ✅ 使用LibreOffice转换PDF成功（最接近Word效果）
```

如果 LibreOffice 未安装，会看到：

```
[PDF预览] LibreOffice未安装，无法使用LibreOffice转换PDF
[PDF预览] LibreOffice不可用，尝试使用WeasyPrint...
```

## ⚠️ 注意事项

1. **内存使用**：LibreOffice 转换会占用一定内存，建议服务器至少 2GB 内存
2. **转换时间**：大文档（>10MB）可能需要 10-30 秒
3. **并发处理**：LibreOffice 支持并发，但建议限制同时转换的数量

## 🐛 故障排查

### 问题1: 找不到 libreoffice 命令

```bash
# 检查是否安装
rpm -qa | grep libreoffice  # CentOS/RHEL
dpkg -l | grep libreoffice  # Ubuntu/Debian

# 如果未安装，重新安装
sudo yum install libreoffice-headless  # CentOS/RHEL
```

### 问题2: 转换失败

检查日志：
```bash
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```

### 问题3: 转换超时

- 检查文档大小（过大可能需要更长时间）
- 检查服务器内存是否充足


