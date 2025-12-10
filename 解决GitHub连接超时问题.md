# 解决 GitHub 连接超时问题

## 🔍 问题分析

错误信息：`Failed to connect to github.com port 443: Connection timed out`

**原因**：
- 服务器无法访问 GitHub 的 HTTPS 端口（443）
- 可能是网络限制或防火墙阻止

---

## 🔧 解决方案

### 方案 1：改用 SSH 协议（推荐）⭐

SSH 使用 22 端口，通常不会被阻止。

#### 步骤 1：检查是否已有 SSH 密钥

```bash
# 检查是否有 SSH 密钥
ls -la ~/.ssh/

# 如果没有，生成一个
ssh-keygen -t ed25519 -C "geshixiugai-server"
# 按 Enter 使用默认路径
```

#### 步骤 2：获取公钥并添加到 GitHub

```bash
# 查看公钥
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容
```

**添加到 GitHub**：
1. 访问：https://github.com/settings/keys
2. 点击 "New SSH key"
3. Title：`阿里云服务器`
4. Key：粘贴公钥
5. 点击 "Add SSH key"

#### 步骤 3：修改 Git 远程地址为 SSH

```bash
# 在服务器上执行
cd /var/www/geshixiugai

# 查看当前远程地址
git remote -v

# 改为 SSH 地址
git remote set-url origin git@github.com:jet20002025-hash/geshixiugai.git

# 验证
git remote -v
# 应该显示：git@github.com:jet20002025-hash/geshixiugai.git

# 测试 SSH 连接
ssh -T git@github.com
# 如果显示 "Hi jet20002025-hash! You've successfully authenticated..." 说明成功

# 尝试拉取
git pull origin main
```

---

### 方案 2：配置 Git 使用代理（如果有代理）

如果你有可用的代理服务器：

```bash
# 配置 HTTP 代理
git config --global http.proxy http://代理地址:端口
git config --global https.proxy https://代理地址:端口

# 或者只针对 GitHub
git config --global http.https://github.com.proxy http://代理地址:端口

# 测试
git pull origin main
```

**取消代理**（如果不需要）：
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

### 方案 3：手动下载代码包（临时方案）

如果网络问题无法解决，可以手动下载：

#### 步骤 1：在本地电脑下载代码

```bash
# 在你的电脑上
cd /Users/zwj/word格式修改器

# 创建代码包
git archive --format=tar.gz --output=geshixiugai.tar.gz main
```

#### 步骤 2：上传到服务器

使用 `scp` 或 `rsync`：

```bash
# 在你的电脑上执行
scp geshixiugai.tar.gz root@121.199.49.1:/tmp/
```

#### 步骤 3：在服务器上解压

```bash
# 在服务器上执行
cd /var/www/geshixiugai

# 备份当前代码（可选）
cp -r . ../geshixiugai_backup_$(date +%Y%m%d)

# 解压新代码
tar -xzf /tmp/geshixiugai.tar.gz -C /tmp/
cp -r /tmp/* /var/www/geshixiugai/

# 重启服务
sudo systemctl restart geshixiugai
```

---

### 方案 4：检查网络和 DNS

#### 检查网络连接

```bash
# 测试 GitHub 连接
ping github.com

# 测试 DNS 解析
nslookup github.com

# 测试 HTTPS 端口
curl -I https://github.com

# 测试 SSH 端口
telnet github.com 22
```

#### 如果 DNS 有问题

```bash
# 修改 DNS 配置
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
echo "nameserver 114.114.114.114" >> /etc/resolv.conf

# 测试
ping github.com
```

---

### 方案 5：使用 GitHub 镜像（如果可用）

某些地区可能有 GitHub 镜像：

```bash
# 尝试使用镜像（如果可用）
git remote set-url origin https://mirror.ghproxy.com/https://github.com/jet20002025-hash/geshixiugai.git

# 或者
git remote set-url origin https://ghproxy.com/https://github.com/jet20002025-hash/geshixiugai.git

# 测试
git pull origin main
```

---

## 🎯 推荐操作流程

### 第一步：尝试 SSH 协议（最可能成功）

```bash
# 1. 检查 SSH 密钥
ls -la ~/.ssh/

# 2. 如果没有，生成一个
ssh-keygen -t ed25519 -C "geshixiugai-server"
cat ~/.ssh/id_ed25519.pub
# 复制公钥，添加到 GitHub

# 3. 修改远程地址
cd /var/www/geshixiugai
git remote set-url origin git@github.com:jet20002025-hash/geshixiugai.git

# 4. 测试连接
ssh -T git@github.com

# 5. 拉取代码
git pull origin main
```

### 第二步：如果 SSH 也不行，检查网络

```bash
# 检查网络连接
ping github.com
curl -I https://github.com
telnet github.com 22
```

### 第三步：如果网络确实无法访问，使用手动方式

在本地打包代码，上传到服务器。

---

## 📋 完整命令（复制粘贴）

### 方案 1：改用 SSH（推荐）

```bash
# 1. 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "geshixiugai-server"
# 按 Enter 使用默认路径

# 2. 查看公钥（复制这个，添加到 GitHub）
cat ~/.ssh/id_ed25519.pub

# 3. 修改远程地址
cd /var/www/geshixiugai
git remote set-url origin git@github.com:jet20002025-hash/geshixiugai.git

# 4. 测试 SSH 连接
ssh -T git@github.com

# 5. 拉取代码
git pull origin main
```

### 方案 2：检查网络

```bash
# 检查网络连接
ping github.com
curl -I https://github.com
telnet github.com 22

# 检查 DNS
nslookup github.com
```

---

## ⚠️ 常见问题

### Q1: SSH 连接也超时？

**A**: 可能是服务器网络完全无法访问 GitHub，需要：
- 检查防火墙设置
- 联系服务器提供商
- 使用代理或手动上传代码

### Q2: 如何检查防火墙？

```bash
# 检查防火墙状态
systemctl status firewalld
# 或
iptables -L

# 如果需要开放端口（需要 root 权限）
firewall-cmd --add-port=22/tcp --permanent
firewall-cmd --reload
```

### Q3: 可以临时使用其他方式吗？

**A**: 可以，使用方案 3（手动下载代码包）

---

## ✅ 验证

### SSH 连接成功

```bash
ssh -T git@github.com
# 应该显示：Hi jet20002025-hash! You've successfully authenticated...
```

### Git 拉取成功

```bash
git pull origin main
# 应该显示更新信息，没有错误
```

---

## 📝 总结

**问题**：HTTPS 端口 443 被阻止

**最佳解决方案**：改用 SSH 协议（端口 22）

**操作步骤**：
1. 生成 SSH 密钥
2. 添加到 GitHub
3. 修改 Git 远程地址为 SSH
4. 测试并拉取代码

**如果 SSH 也不行**：检查网络或使用手动上传方式

---

**现在执行：先尝试方案 1（改用 SSH），这是最可能成功的方案！** 🚀




