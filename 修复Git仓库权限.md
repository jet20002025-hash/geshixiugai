# 修复 Git 仓库权限

## 🔍 问题

Git 仓库目录权限不正确，无法拉取代码。

---

## ✅ 解决方案

### 方法 1：修复目录权限（推荐）

```bash
# 修复项目目录权限
sudo chown -R admin:admin /var/www/geshixiugai

# 然后拉取代码
cd /var/www/geshixiugai
git pull origin main
```

### 方法 2：使用 sudo 拉取（临时方案）

```bash
cd /var/www/geshixiugai
sudo git pull origin main
```

---

## 🚀 推荐操作流程

```bash
# 1. 修复目录权限
sudo chown -R admin:admin /var/www/geshixiugai

# 2. 添加安全目录配置
git config --global --add safe.directory /var/www/geshixiugai

# 3. 拉取最新代码
cd /var/www/geshixiugai
git pull origin main

# 4. 重启服务
sudo systemctl restart geshixiugai

# 5. 检查服务状态
sudo systemctl status geshixiugai
```

---

## ⚠️ 注意事项

修复权限后，确保以下目录的权限正确：
- `/var/www/geshixiugai/storage` - 应该是 nginx:nginx
- `/var/www/geshixiugai/venv` - 可以是 admin:admin
- `/var/www/geshixiugai/.env` - 应该是 nginx:nginx（服务需要读取）

如果修复权限后服务无法读取 .env，需要：
```bash
sudo chown nginx:nginx /var/www/geshixiugai/.env
```

---

**先执行权限修复命令！** 🔧





