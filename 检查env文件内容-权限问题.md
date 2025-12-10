# 检查 .env 文件内容 - 权限问题

## 🔍 问题

`.env` 文件权限是 `600`，所有者是 `nginx`，`admin` 用户无法直接读取。

---

## ✅ 解决方案

### 方法 1：使用 sudo 查看文件内容

```bash
# 使用 sudo 查看配置项（隐藏值）
sudo grep "^ALIPAY" /var/www/geshixiugai/.env | sed 's/=.*/=***/'
```

### 方法 2：检查配置项是否存在

```bash
# 检查是否有 ALIPAY 配置
sudo grep "^ALIPAY" /var/www/geshixiugai/.env
```

### 方法 3：查看文件完整内容（注意：会显示敏感信息）

```bash
sudo cat /var/www/geshixiugai/.env
```

---

## 🔧 如果配置不存在或格式错误

### 编辑 .env 文件

```bash
# 使用 sudo 编辑文件
sudo vi /var/www/geshixiugai/.env
```

或者：

```bash
# 切换到 root 用户编辑
sudo su -
cd /var/www/geshixiugai
vi .env
```

### 添加支付宝配置

在文件末尾添加：

```bash
# 支付宝支付配置
ALIPAY_APP_ID=你的支付宝AppID
ALIPAY_PRIVATE_KEY=你的应用私钥（完整内容）
ALIPAY_PUBLIC_KEY=支付宝公钥（完整内容）
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do
BASE_URL=https://geshixiugai.cn
```

保存退出后：

```bash
# 确保文件权限正确
sudo chown nginx:nginx /var/www/geshixiugai/.env
sudo chmod 600 /var/www/geshixiugai/.env

# 重启服务
sudo systemctl restart geshixiugai
```

---

## 📋 完整排查命令

```bash
# 1. 检查配置项是否存在（使用 sudo）
sudo grep "^ALIPAY" /var/www/geshixiugai/.env | sed 's/=.*/=***/'

# 2. 如果没看到输出，说明配置不存在，需要添加
# 3. 如果看到输出，检查配置格式是否正确

# 4. 重启服务
sudo systemctl restart geshixiugai

# 5. 查看日志
sudo tail -n 50 /var/log/geshixiugai/error.log | grep -i alipay
```

---

**先使用 sudo 检查配置是否存在！** 🔍





