# 安装 Git 并继续部署

## 🔍 问题

服务器提示：`git: command not found`

**原因**：服务器上没有安装 Git。

---

## ✅ 解决方案

### 步骤 1：安装 Git

根据你的系统类型，执行相应的安装命令：

#### 如果是 CentOS/RHEL 系统（你的服务器可能是这个）

```bash
# 安装 Git
sudo dnf install -y git

# 或者如果是 CentOS 7
sudo yum install -y git
```

#### 如果是 Ubuntu/Debian 系统

```bash
sudo apt update
sudo apt install -y git
```

### 步骤 2：验证安装

```bash
git --version
```

如果显示版本号（如 `git version 2.x.x`），说明安装成功。

### 步骤 3：继续克隆代码

```bash
cd /var/www
git clone https://github.com/jet20002025-hash/geshixiugai.git geshixiugai
```

### 步骤 4：继续部署

克隆完成后，执行：

```bash
cd geshixiugai
chmod +x deploy_aliyun.sh
sudo ./deploy_aliyun.sh
```

---

## 🚀 完整命令序列

在服务器上依次执行：

```bash
# 1. 安装 Git（CentOS/RHEL）
sudo dnf install -y git
# 或者如果是 CentOS 7：sudo yum install -y git

# 2. 验证安装
git --version

# 3. 克隆代码
cd /var/www
git clone https://github.com/jet20002025-hash/geshixiugai.git geshixiugai

# 4. 进入项目目录
cd geshixiugai

# 5. 运行部署脚本
chmod +x deploy_aliyun.sh
sudo ./deploy_aliyun.sh
```

---

## 🔍 判断系统类型

如果不确定系统类型，可以执行：

```bash
cat /etc/os-release
```

根据输出判断：
- 如果显示 `CentOS` 或 `Red Hat` → 使用 `dnf` 或 `yum`
- 如果显示 `Ubuntu` 或 `Debian` → 使用 `apt`

---

## ⚠️ 注意事项

1. **如果是 CentOS 8+**：使用 `dnf` 命令
2. **如果是 CentOS 7**：使用 `yum` 命令
3. **如果是 Ubuntu**：先执行 `apt update`，再 `apt install`

---

**先安装 Git，然后继续部署！** 🚀




