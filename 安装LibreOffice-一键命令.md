# 安装 LibreOffice - 一键命令

## 🚀 快速安装（推荐）

在服务器上执行以下命令：

```bash
# CentOS/RHEL/Alibaba Cloud Linux
sudo yum install -y libreoffice-headless

# 验证安装
libreoffice --version

# 重启服务
cd /var/www/geshixiugai
sudo systemctl restart geshixiugai
```

## 📋 完整步骤

```bash
# 1. 安装 LibreOffice（无界面版本，适合服务器）
sudo yum install -y libreoffice-headless

# 2. 验证安装
which libreoffice
libreoffice --version

# 3. 测试转换（可选）
cd /tmp
echo "测试文档" > test.txt
libreoffice --headless --convert-to pdf test.txt
ls -lh test.pdf

# 4. 重启服务
cd /var/www/geshixiugai
sudo systemctl restart geshixiugai

# 5. 查看日志
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```

## ✅ 安装后验证

安装完成后，重新上传一个文档，应该看到：

```
[PDF预览] 执行LibreOffice PDF转换命令: libreoffice --headless --convert-to pdf ...
[PDF预览] LibreOffice PDF转换成功，大小: XXX KB
[PDF预览] ✅ 使用LibreOffice转换PDF成功（最接近Word效果）
```

## ⚠️ 如果安装失败

### 问题1: 找不到 libreoffice-headless 包

```bash
# 尝试安装完整版
sudo yum install -y libreoffice

# 或者使用 EPEL 仓库
sudo yum install -y epel-release
sudo yum install -y libreoffice-headless
```

### 问题2: 依赖冲突

```bash
# 查看详细信息
sudo yum install -y libreoffice-headless --verbose

# 或者强制安装
sudo yum install -y libreoffice-headless --skip-broken
```

## 📊 系统要求

- **内存**：建议至少 2GB 可用内存
- **磁盘**：LibreOffice 大约需要 500MB 磁盘空间
- **CPU**：无特殊要求

## 🔄 如果不想安装 LibreOffice

如果由于某些原因无法安装 LibreOffice，我们可以：
1. 改进 HTML 预览（让它更接近 Word）
2. 使用其他 PDF 生成库
3. 修复 WeasyPrint 的 transform 错误（需要更多调试）

但**强烈建议安装 LibreOffice**，因为它能提供最接近 Word 的预览效果。




