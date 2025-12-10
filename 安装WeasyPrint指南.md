# 安装 WeasyPrint 指南

## 📍 在哪里执行命令？

**在阿里云服务器的远程连接终端里执行！**

---

## 🚀 详细步骤

### 步骤 1：打开阿里云控制台远程连接

1. **访问阿里云控制台**
   - 网址：https://ecs.console.aliyun.com/
   - 登录你的账号

2. **找到你的服务器**
   - 服务器IP：`121.199.49.1`
   - 点击服务器名称进入详情页

3. **打开远程连接**
   - 点击页面上的 **"远程连接"** 按钮
   - 选择 **"Workbench远程连接"**
   - 输入 root 密码登录

4. **确认位置**
   - 你会看到类似这样的提示符：
   ```bash
   [root@iZbp1fic2d7eob78hrzn0hZ ~]#
   ```
   - **这就是正确的位置！**

---

### 步骤 2：进入项目目录

在远程连接的终端里，执行：

```bash
# 进入项目目录
cd /var/www/geshixiugai
```

---

### 步骤 3：激活虚拟环境（如果有）

如果你的项目使用了虚拟环境，先激活它：

```bash
# 检查是否有虚拟环境
ls -la | grep venv

# 如果有虚拟环境，激活它（根据实际情况调整路径）
source venv/bin/activate
# 或
source .venv/bin/activate
```

**如何判断是否需要激活虚拟环境？**
- 如果提示符前面有 `(venv)` 或 `(.venv)`，说明已经激活
- 如果没有，尝试激活（如果报错说明没有虚拟环境，直接执行下一步）

---

### 步骤 4：安装 WeasyPrint

在远程连接的终端里，执行：

```bash
# 安装 weasyprint
pip install weasyprint
```

**如果提示权限错误，使用：**
```bash
pip install --user weasyprint
```

**或者如果使用虚拟环境：**
```bash
# 确保虚拟环境已激活
source venv/bin/activate  # 或 source .venv/bin/activate

# 安装
pip install weasyprint
```

---

### 步骤 5：安装系统依赖（可选，但推荐）

WeasyPrint 需要系统字体支持，建议安装：

**Ubuntu/Debian 系统：**
```bash
sudo apt update
sudo apt install -y fonts-liberation
```

**CentOS/RHEL 系统：**
```bash
sudo yum install -y liberation-fonts
```

---

### 步骤 6：验证安装

```bash
# 测试 weasyprint 是否安装成功
python -c "import weasyprint; print('WeasyPrint 安装成功！版本:', weasyprint.__version__)"
```

如果看到版本号，说明安装成功！

---

### 步骤 7：更新代码（如果需要）

如果代码已经更新到 GitHub，拉取最新代码：

```bash
# 确保在项目目录
cd /var/www/geshixiugai

# 拉取最新代码
git pull origin main
```

---

### 步骤 8：重启服务

安装完成后，重启服务使更改生效：

```bash
# 重启服务
sudo systemctl restart geshixiugai

# 检查服务状态
sudo systemctl status geshixiugai
```

---

## 📋 完整命令清单

**在阿里云控制台的远程连接终端里，依次执行：**

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 激活虚拟环境（如果有）
source venv/bin/activate  # 或 source .venv/bin/activate

# 3. 安装 weasyprint
pip install weasyprint

# 4. 安装系统字体（推荐）
sudo apt update
sudo apt install -y fonts-liberation

# 5. 验证安装
python -c "import weasyprint; print('安装成功！版本:', weasyprint.__version__)"

# 6. 更新代码（如果需要）
git pull origin main

# 7. 重启服务
sudo systemctl restart geshixiugai
```

---

## ❓ 常见问题

### Q1: 提示 "pip: command not found"

**解决方法：**
```bash
# 使用 python3 -m pip
python3 -m pip install weasyprint

# 或安装 pip
sudo apt install python3-pip  # Ubuntu/Debian
sudo yum install python3-pip  # CentOS
```

### Q2: 提示权限错误

**解决方法：**
```bash
# 使用 --user 参数
pip install --user weasyprint

# 或使用 sudo（不推荐，但可以）
sudo pip install weasyprint
```

### Q3: 安装很慢或失败

**解决方法：**
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint
```

### Q4: 导入 weasyprint 报错

**可能原因：**
- 系统缺少字体库
- 缺少系统依赖

**解决方法：**
```bash
# Ubuntu/Debian
sudo apt install -y fonts-liberation libpango-1.0-0 libpangoft2-1.0-0

# CentOS
sudo yum install -y liberation-fonts pango
```

---

## ✅ 验证安装成功

安装完成后，重新处理一个文档，查看日志：

```bash
# 查看服务日志
sudo journalctl -u geshixiugai -f
```

如果看到：
```
[PDF预览] PDF生成成功，大小: 123.45 KB
```

说明 WeasyPrint 工作正常！

---

## 📝 总结

1. **在哪里执行**：阿里云控制台的远程连接终端
2. **执行什么**：`pip install weasyprint`
3. **在哪里执行**：项目目录 `/var/www/geshixiugai`
4. **执行后**：重启服务 `sudo systemctl restart geshixiugai`

**记住：所有命令都在阿里云控制台的网页对话框里执行！** 🎯



