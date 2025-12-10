# 修复 storage 目录权限

## 🔍 问题

代码尝试创建 `storage` 目录，但 nginx 用户没有权限。

错误信息：
```
PermissionError: [Errno 13] Permission denied: 'storage'
```

---

## ✅ 解决方案

### 步骤 1：创建 storage 目录

```bash
cd /var/www/geshixiugai
sudo mkdir -p storage/templates
sudo mkdir -p storage/documents
```

### 步骤 2：设置目录权限

```bash
# 设置所有者为 nginx（CentOS/RHEL/Alinux）
sudo chown -R nginx:nginx /var/www/geshixiugai/storage

# 设置目录权限
sudo chmod -R 755 /var/www/geshixiugai/storage
```

### 步骤 3：验证权限

```bash
ls -la /var/www/geshixiugai/storage
```

### 步骤 4：重启服务

```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

---

## 🚀 完整修复命令（复制粘贴）

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 创建 storage 目录结构
sudo mkdir -p storage/templates
sudo mkdir -p storage/documents

# 3. 设置权限（nginx 用户）
sudo chown -R nginx:nginx storage

# 4. 设置目录权限
sudo chmod -R 755 storage

# 5. 验证权限
ls -la storage

# 6. 重启服务
sudo systemctl restart geshixiugai

# 7. 检查服务状态
sudo systemctl status geshixiugai
```

---

## ✅ 预期结果

修复后，服务应该能正常启动：

```bash
sudo systemctl status geshixiugai
```

应该显示：
```
Active: active (running)
```

---

**先执行修复命令！** 🔧





