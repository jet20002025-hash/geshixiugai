# LibreOffice 安装指南

## 📋 为什么需要 LibreOffice？

为了生成与 Word 文档**一模一样**的预览，我们使用 LibreOffice 来转换文档。LibreOffice 可以：
- ✅ 保留所有格式（字体、颜色、表格、图片等）
- ✅ 保留页面布局
- ✅ 保留页眉页脚
- ✅ 保留所有样式

如果没有安装 LibreOffice，系统会自动回退到自定义 HTML 生成（功能较简单）。

---

## 🚀 安装步骤

### Ubuntu/Debian 系统

```bash
# 更新软件包列表
sudo apt update

# 安装 LibreOffice（无界面版本，适合服务器）
sudo apt install -y libreoffice --no-install-recommends

# 验证安装
libreoffice --version
# 或
soffice --version
```

### CentOS/RHEL 系统

```bash
# 安装 LibreOffice
sudo yum install -y libreoffice-headless

# 验证安装
libreoffice --version
```

### macOS 系统

```bash
# 使用 Homebrew 安装
brew install --cask libreoffice

# 验证安装
/Applications/LibreOffice.app/Contents/MacOS/soffice --version
```

### 使用 Docker

如果使用 Docker 部署，在 Dockerfile 中添加：

```dockerfile
# Ubuntu 基础镜像
RUN apt-get update && \
    apt-get install -y libreoffice --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 验证
RUN libreoffice --version
```

---

## ✅ 验证安装

安装完成后，运行以下命令验证：

```bash
# 方法1: 检查命令是否存在
which libreoffice
which soffice

# 方法2: 查看版本
libreoffice --version
soffice --version

# 方法3: 测试转换（可选）
echo "测试" > test.txt
libreoffice --headless --convert-to html test.txt
```

---

## 🔧 配置说明

### 系统会自动检测

代码会自动检测系统中是否安装了 LibreOffice：
- 如果安装了：使用 LibreOffice 转换（格式完美保留）
- 如果未安装：使用自定义 HTML 生成（基本格式）

### 手动指定 LibreOffice 路径

如果需要指定 LibreOffice 的路径，可以在环境变量中设置：

```bash
export LIBREOFFICE_CMD=/usr/bin/libreoffice
# 或
export LIBREOFFICE_CMD=/Applications/LibreOffice.app/Contents/MacOS/soffice
```

---

## 📊 性能对比

| 转换方式 | 格式保留度 | 速度 | 依赖 |
|---------|-----------|------|------|
| **LibreOffice** | ⭐⭐⭐⭐⭐ 完美 | 中等 | 需要安装 |
| 自定义HTML | ⭐⭐⭐ 基本 | 快 | 无 |

---

## ⚠️ 注意事项

1. **内存使用**：LibreOffice 转换会占用一定内存，建议服务器至少 2GB 内存
2. **转换时间**：大文档（>10MB）可能需要 10-30 秒
3. **并发处理**：LibreOffice 支持并发，但建议限制同时转换的数量

---

## 🐛 故障排查

### 问题1: 找不到 libreoffice 命令

**解决方法：**
```bash
# 检查是否安装
dpkg -l | grep libreoffice  # Ubuntu/Debian
rpm -qa | grep libreoffice  # CentOS/RHEL

# 如果未安装，重新安装
sudo apt install libreoffice  # Ubuntu/Debian
```

### 问题2: 转换失败

**检查日志：**
- 查看后端日志中的 `[HTML预览]` 相关信息
- 检查文档是否损坏
- 检查磁盘空间是否充足

### 问题3: 转换超时

**解决方法：**
- 检查文档大小（过大可能需要更长时间）
- 增加超时时间（代码中默认 60 秒）

---

## 📝 测试

安装完成后，重新处理一个文档，查看日志：

```
[HTML预览] 执行LibreOffice转换命令: libreoffice --headless --convert-to html ...
[HTML预览] LibreOffice转换成功，HTML大小: 123.45 KB
```

如果看到这些日志，说明 LibreOffice 转换正常工作！

---

## 🔗 相关链接

- [LibreOffice 官网](https://www.libreoffice.org/)
- [LibreOffice 命令行文档](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html)


