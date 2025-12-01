# 配置 SSL 证书 - HTTPS

## ✅ 当前状态

- [x] 网站已可访问：http://geshixiugai.cn
- [ ] 配置 HTTPS（SSL 证书）

---

## 🚀 配置 SSL 证书步骤

### 在服务器上执行（阿里云控制台的对话框里）

```bash
# 1. 安装 Certbot
sudo dnf install -y certbot python3-certbot-nginx

# 2. 申请 SSL 证书（会自动配置 Nginx）
sudo certbot --nginx -d geshixiugai.cn -d www.geshixiugai.cn
```

### 按照提示操作

1. **输入邮箱地址**（用于证书到期提醒）
2. **同意服务条款**：输入 `Y`
3. **是否接收邮件通知**：可选，输入 `Y` 或 `N`
4. **等待验证完成**（通常几秒钟）

Certbot 会自动：
- 验证域名所有权
- 申请证书
- 配置 Nginx
- 设置 HTTP 到 HTTPS 的重定向

---

## ✅ 验证 HTTPS

配置完成后，在浏览器中访问：
- `https://geshixiugai.cn`
- `https://www.geshixiugai.cn`

应该看到：
- ✅ 绿色锁图标
- ✅ HTTPS 连接
- ✅ 证书有效

---

## 🔧 测试自动续期

```bash
# 测试证书续期（不会实际续期）
sudo certbot renew --dry-run
```

证书每 90 天自动续期，无需手动操作。

---

## 📋 完整命令（复制粘贴）

```bash
# 1. 安装 Certbot
sudo dnf install -y certbot python3-certbot-nginx

# 2. 申请证书
sudo certbot --nginx -d geshixiugai.cn -d www.geshixiugai.cn

# 3. 测试自动续期
sudo certbot renew --dry-run
```

---

## 🎉 配置完成后

- ✅ HTTP 会自动重定向到 HTTPS
- ✅ 访问 http://geshixiugai.cn 会自动跳转到 https://geshixiugai.cn
- ✅ 证书每 90 天自动续期

---

**现在配置 SSL 证书，让网站支持 HTTPS！** 🔒


