# 修复 Git 权限并更新代码

## 🔍 问题

Git 检测到仓库所有者不匹配，需要添加安全目录配置。

---

## ✅ 解决方案

### 步骤 1：添加安全目录配置

```bash
git config --global --add safe.directory /var/www/geshixiugai
```

### 步骤 2：拉取最新代码

```bash
git pull origin main
```

### 步骤 3：重启服务

```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

---

## 📋 完整命令（复制粘贴）

```bash
# 1. 修复 Git 权限
git config --global --add safe.directory /var/www/geshixiugai

# 2. 拉取最新代码
git pull origin main

# 3. 重启服务
sudo systemctl restart geshixiugai

# 4. 检查服务状态
sudo systemctl status geshixiugai
```

---

## ✅ 验证

在浏览器中访问 `https://geshixiugai.cn`，滚动到页面底部，应该看到备案号。

---

**现在执行修复命令！** 🔧








