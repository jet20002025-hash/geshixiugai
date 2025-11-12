# DNS 配置检查清单

## 检查步骤

### 第一步：检查 Vercel 域名配置

**在 Vercel 中：**
1. 登录 Vercel Dashboard
2. 进入项目 `geshixiugai-app`
3. 点击 **Settings** → **Domains**
4. 检查是否已添加 `geshixiugai.org`
5. 查看域名状态：
   - ✅ **Valid Configuration** - 配置正确
   - ⚠️ **Pending** - 等待 DNS 生效
   - ❌ **Invalid Configuration** - 配置错误

**应该看到：**
```
geshixiugai.org
Status: Valid Configuration
指向: cname.vercel-dns.com
```

---

### 第二步：检查 Cloudflare DNS 记录

**在 Cloudflare 中：**
1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择域名 `geshixiugai.org`
3. 进入 **DNS** → **Records**
4. 检查是否有以下记录：

**记录 1（根域名）：**
```
类型: CNAME
名称: @
内容: cname.vercel-dns.com
代理状态: ✅ 已代理（橙色云朵）
TTL: Auto
```

**记录 2（www 子域名）：**
```
类型: CNAME
名称: www
内容: cname.vercel-dns.com
代理状态: ✅ 已代理（橙色云朵）
TTL: Auto
```

**重要检查点：**
- ✅ 类型必须是 **CNAME**（不是 A 记录）
- ✅ 内容必须是 `cname.vercel-dns.com`
- ✅ 代理状态必须是 **已代理**（橙色云朵，不是灰色）

---

### 第三步：检查 DNS 传播状态

**使用在线工具检查：**

1. **DNS Checker**
   - 访问：https://dnschecker.org/
   - 输入域名：`geshixiugai.org`
   - 选择记录类型：**CNAME**
   - 点击 "Search"
   - 查看全球 DNS 解析情况

2. **检查结果应该显示：**
   - 大部分地区显示：`cname.vercel-dns.com`
   - 如果显示其他值或错误，说明 DNS 未生效

---

### 第四步：使用命令行检查

**在终端执行：**

```bash
# 检查 CNAME 记录
nslookup -type=CNAME geshixiugai.org

# 或使用 dig
dig geshixiugai.org CNAME

# 检查 A 记录（应该指向 Cloudflare IP）
dig geshixiugai.org A
```

**预期结果：**
- CNAME 记录应该指向 `cname.vercel-dns.com`
- A 记录应该显示 Cloudflare 的 IP 地址（如果代理开启）

---

### 第五步：测试访问

**访问测试：**

1. **访问根域名：**
   ```
   https://geshixiugai.org
   ```
   - 应该能看到前端页面
   - 不应该显示 "Not Found" 或错误

2. **访问 www 子域名：**
   ```
   https://www.geshixiugai.org
   ```
   - 应该也能正常访问

3. **检查 SSL 证书：**
   - 浏览器地址栏应该显示绿色锁图标
   - 证书应该有效（不是自签名）

---

## 常见问题检查

### 问题1: DNS 记录不存在

**症状：**
- Vercel 显示 "Invalid Configuration"
- 访问域名显示 "Not Found"

**解决方法：**
1. 在 Cloudflare 添加 CNAME 记录
2. 确保代理状态开启（橙色云朵）
3. 等待 DNS 传播（5 分钟到 24 小时）

---

### 问题2: 代理状态未开启

**症状：**
- DNS 记录存在，但访问很慢或无法访问
- 直接指向 Vercel，没有经过 Cloudflare CDN

**解决方法：**
1. 在 Cloudflare DNS 记录中
2. 点击记录右侧的云朵图标
3. 确保是橙色（已代理），不是灰色（仅 DNS）

---

### 问题3: DNS 未生效

**症状：**
- 配置正确，但访问还是失败
- DNS Checker 显示旧记录或错误

**解决方法：**
1. 等待更长时间（最多 24 小时）
2. 清除本地 DNS 缓存：
   ```bash
   # macOS
   sudo dscacheutil -flushcache
   sudo killall -HUP mDNSResponder
   
   # Windows
   ipconfig /flushdns
   ```
3. 使用不同网络测试

---

### 问题4: SSL 证书问题

**症状：**
- 访问显示 "不安全连接"
- 证书错误

**解决方法：**
1. 在 Cloudflare 中，确保 SSL/TLS 设置为：
   - **Full** 或 **Full (strict)**
   - 不是 "Flexible"
2. 等待 SSL 证书自动配置（通常几分钟）
3. 清除浏览器缓存后重试

---

## 快速检查命令

**一键检查脚本：**

```bash
#!/bin/bash
echo "=== DNS 配置检查 ==="
echo ""
echo "1. 检查 CNAME 记录："
nslookup -type=CNAME geshixiugai.org | grep -A 2 "canonical name"
echo ""
echo "2. 检查 A 记录："
dig +short geshixiugai.org A
echo ""
echo "3. 检查 HTTPS 连接："
curl -I https://geshixiugai.org 2>&1 | head -5
```

---

## 配置正确标准

✅ **所有检查项都通过：**

- [x] Vercel 中域名状态为 "Valid Configuration"
- [x] Cloudflare 中有正确的 CNAME 记录
- [x] 代理状态开启（橙色云朵）
- [x] DNS 已传播到全球
- [x] 可以访问 https://geshixiugai.org
- [x] SSL 证书有效
- [x] 前端页面正常显示

---

## 需要帮助？

如果检查后发现配置有问题，请告诉我：
1. Vercel 域名状态是什么？
2. Cloudflare DNS 记录是什么样的？
3. 访问域名时看到什么错误？

我可以帮你进一步排查。

