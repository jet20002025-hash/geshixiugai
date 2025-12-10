# 阿里云服务器安装 LibreOffice 指南

## 🚀 快速安装（推荐）

### 方式一：使用安装脚本（最简单）

```bash
# 1. 上传脚本到服务器（或直接在服务器上创建）
# 2. 执行安装脚本
cd /var/www/geshixiugai
chmod +x install_libreoffice_server.sh
sudo ./install_libreoffice_server.sh
```

### 方式二：手动安装命令

#### 如果是 CentOS/RHEL/Alibaba Cloud Linux：

```bash
# 安装 LibreOffice（无界面版本，适合服务器）
sudo yum install -y libreoffice-headless

# 如果上面命令失败，尝试安装完整版
sudo yum install -y libreoffice
```

#### 如果是 Ubuntu/Debian：

```bash
# 更新软件包列表
sudo apt update

# 安装 LibreOffice（无推荐依赖，减少体积）
sudo apt install -y libreoffice --no-install-recommends
```

---

## ✅ 验证安装

安装完成后，验证 LibreOffice 是否可用：

```bash
# 检查命令是否存在
which libreoffice
which soffice

# 查看版本
libreoffice --version
# 或
soffice --version
```

**预期输出示例：**
```
LibreOffice 7.1.8.1 10(Build:1)
```

---

## 🔄 更新代码并重启服务

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 拉取最新代码（包含 macOS 路径支持）
git pull origin main

# 3. 重启服务
sudo systemctl restart geshixiugai

# 4. 检查服务状态
sudo systemctl status geshixiugai
```

---

## 📊 查看日志验证

实时查看 PDF 转换日志：

```bash
sudo journalctl -u geshixiugai -f | grep -E "\[PDF预览\]"
```

**成功时的日志示例：**
```
[PDF预览] 找到LibreOffice命令: /usr/bin/libreoffice
[PDF预览] 执行LibreOffice PDF转换命令: libreoffice --headless --convert-to pdf ...
[PDF预览] LibreOffice PDF转换成功，大小: XXX KB
[PDF预览] ✅ 使用LibreOffice转换PDF成功（最接近Word效果）
```

---

## 🧪 测试转换功能

### 方法 1：使用网页测试工具

1. 访问：https://www.geshixiugai.cn/web/convert.html
2. 上传一个 Word 文档
3. 点击"开始转换"
4. 如果转换成功，会自动下载 PDF 文件

### 方法 2：命令行测试

```bash
# 创建测试文件
cd /tmp
echo "测试文档内容" > test.txt

# 测试转换
libreoffice --headless --convert-to pdf test.txt

# 检查是否生成 PDF
ls -lh test.pdf
```

---

## ⚠️ 常见问题

### 问题 1：找不到 libreoffice-headless 包

**解决方案：**
```bash
# CentOS/RHEL: 尝试安装完整版
sudo yum install -y libreoffice

# 或者启用 EPEL 仓库
sudo yum install -y epel-release
sudo yum install -y libreoffice-headless
```

### 问题 2：安装后仍显示"LibreOffice未找到"

**检查步骤：**

1. **确认安装路径：**
   ```bash
   which libreoffice
   which soffice
   ```

2. **检查服务运行用户：**
   ```bash
   ps aux | grep gunicorn
   ```

3. **检查文件权限：**
   ```bash
   ls -l /usr/bin/libreoffice
   sudo chmod +x /usr/bin/libreoffice  # 如果需要
   ```

4. **检查 PATH 环境变量：**
   ```bash
   sudo systemctl show geshixiugai | grep Environment
   ```

### 问题 3：转换超时或失败

**可能原因：**
- 文档太大或格式复杂
- 内存不足
- 文件权限问题

**解决方案：**
```bash
# 查看详细错误日志
sudo journalctl -u geshixiugai -n 100 | grep -E "\[PDF预览\]|错误|Error"

# 检查系统资源
free -h
df -h
```

---

## 📋 系统要求

- **内存**：建议至少 2GB 可用内存
- **磁盘**：LibreOffice 大约需要 500MB 磁盘空间
- **CPU**：无特殊要求

---

## 🔧 卸载 LibreOffice（如果需要）

```bash
# CentOS/RHEL
sudo yum remove -y libreoffice-headless

# Ubuntu/Debian
sudo apt remove -y libreoffice
```

---

## 📞 需要帮助？

如果安装或使用过程中遇到问题，请查看：
- 服务日志：`sudo journalctl -u geshixiugai -f`
- 安装日志：`/tmp/libreoffice_install.log`（如果使用脚本安装）

