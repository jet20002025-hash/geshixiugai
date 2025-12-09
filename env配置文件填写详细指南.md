# .env 配置文件填写详细指南

## 📋 配置说明

你需要至少配置**一种存储方案**（Supabase Storage 或 Cloudflare R2），支付配置是可选的。

---

## 🎯 方案 1：使用 Supabase Storage（推荐 ⭐）

### 为什么推荐 Supabase？
- ✅ 免费额度充足（1GB 存储，2GB 流量/月）
- ✅ 国内访问相对稳定
- ✅ 配置简单，5分钟完成

### 步骤 1：注册 Supabase（如果没有账号）

1. 访问：https://supabase.com
2. 点击 "Start your project"
3. 使用 GitHub 账号登录（推荐）
4. 创建新项目：
   - **Name**：`word-formatter`（任意名称）
   - **Database Password**：设置密码（**请保存好！**）
   - **Region**：选择 `Southeast Asia (Singapore)`（离中国最近）
5. 点击 "Create new project"
6. 等待项目创建完成（约 1-2 分钟）

### 步骤 2：创建 Storage Bucket

1. 在 Supabase Dashboard 左侧菜单，点击 **"Storage"**
2. 点击 **"Create a new bucket"** 或 **"New bucket"**
3. 填写信息：
   - **Name**：`word-formatter-storage`
   - **Public bucket**：**取消勾选**（私有存储，更安全）
4. 点击 **"Create bucket"**

### 步骤 3：获取 API Key

1. 在 Supabase Dashboard 左侧菜单，点击 **"Settings"**（齿轮图标）
2. 点击 **"API"**
3. 找到 **"service_role" `secret`** key
4. 点击 **"Reveal"** 显示完整 key
5. **立即复制保存**以下信息：
   - **Project URL**：类似 `https://xxxxxxxxxxxxx.supabase.co` → 这就是 `SUPABASE_URL`
   - **`service_role` `secret` key**：长字符串 → 这就是 `SUPABASE_KEY`

### 步骤 4：填写 .env 文件

在服务器上编辑 `.env` 文件：

```bash
cd /var/www/geshixiugai
vi .env
```

填入以下内容（**删除所有注释和示例**）：

```bash
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=你的service_role key（完整的长字符串）
SUPABASE_BUCKET=word-formatter-storage
```

**示例**（替换为你的实际值）：
```bash
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjE2MjM5MDIyLCJleHAiOjE5MzE4MTUwMjJ9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SUPABASE_BUCKET=word-formatter-storage
```

---

## 🎯 方案 2：使用 Cloudflare R2

### 步骤 1：登录 Cloudflare Dashboard

1. 访问：https://dash.cloudflare.com
2. 使用你的账号登录

### 步骤 2：创建 R2 Bucket

1. 点击左侧菜单 **"R2"**
2. 点击 **"Create bucket"**
3. 填写信息：
   - **Bucket name**：`word-formatter-storage`
   - **Location**：选择离你最近的区域（如 `APAC`）
4. 点击 **"Create bucket"**

### 步骤 3：创建 API Token

1. 在 R2 页面，点击 **"Manage R2 API Tokens"**
2. 点击 **"Create API token"**
3. 选择 **"S3 API"** 或 **"Custom token"**
4. 设置权限：
   - **Permissions**：Read and Write
   - **Bucket**：选择 `word-formatter-storage`
5. 点击 **"Create API token"**
6. **立即复制保存**（只显示一次）：
   - **Access Key ID** → `R2_ACCESS_KEY_ID`
   - **Secret Access Key** → `R2_SECRET_ACCESS_KEY`
   - **Account ID** → `R2_ACCOUNT_ID`（在 R2 页面顶部可以看到）
   - **Endpoint** → `R2_ENDPOINT`（格式：`https://你的Account ID.r2.cloudflarestorage.com`）

### 步骤 4：填写 .env 文件

```bash
R2_ACCOUNT_ID=你的Account ID（如：5003936d05d7bc23217a0fdef979a238）
R2_ACCESS_KEY_ID=你的Access Key ID
R2_SECRET_ACCESS_KEY=你的Secret Access Key
R2_BUCKET_NAME=word-formatter-storage
R2_ENDPOINT=https://你的Account ID.r2.cloudflarestorage.com
```

**示例**：
```bash
R2_ACCOUNT_ID=5003936d05d7bc23217a0fdef979a238
R2_ACCESS_KEY_ID=f663cb46e66524d71351020dada457e1
R2_SECRET_ACCESS_KEY=a56af737607a72d8dc77630a9bd476acdc9ca2e07b752f39bda00d137d8f94f7
R2_BUCKET_NAME=word-formatter-storage
R2_ENDPOINT=https://5003936d05d7bc23217a0fdef979a238.r2.cloudflarestorage.com
```

---

## 💰 支付配置（可选）

如果你已经配置了支付宝支付，可以填写：

### 获取支付宝配置信息

1. 登录支付宝开放平台：https://open.alipay.com/
2. 进入你的应用
3. 获取：
   - **AppID** → `ALIPAY_APP_ID`
   - **应用私钥** → `ALIPAY_PRIVATE_KEY`（需要保留换行符）
   - **支付宝公钥** → `ALIPAY_PUBLIC_KEY`

### 填写 .env 文件

```bash
ALIPAY_APP_ID=你的支付宝AppID
ALIPAY_PRIVATE_KEY=你的支付宝私钥（完整内容，包括BEGIN和END行）
ALIPAY_PUBLIC_KEY=支付宝公钥（完整内容，包括BEGIN和END行）
```

**注意**：私钥和公钥需要保留完整的格式，包括：
```
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
```

---

## 📝 完整的 .env 文件示例

### 示例 1：使用 Supabase Storage

```bash
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjE2MjM5MDIyLCJleHAiOjE5MzE4MTUwMjJ9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SUPABASE_BUCKET=word-formatter-storage
```

### 示例 2：使用 Cloudflare R2

```bash
R2_ACCOUNT_ID=5003936d05d7bc23217a0fdef979a238
R2_ACCESS_KEY_ID=f663cb46e66524d71351020dada457e1
R2_SECRET_ACCESS_KEY=a56af737607a72d8dc77630a9bd476acdc9ca2e07b752f39bda00d137d8f94f7
R2_BUCKET_NAME=word-formatter-storage
R2_ENDPOINT=https://5003936d05d7bc23217a0fdef979a238.r2.cloudflarestorage.com
```

### 示例 3：Supabase + 支付宝支付

```bash
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_BUCKET=word-formatter-storage

ALIPAY_APP_ID=2021001234567890
ALIPAY_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
ALIPAY_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
-----END PUBLIC KEY-----
```

---

## ⚠️ 重要提示

1. **只配置一种存储方案**：
   - 要么用 Supabase（填写 SUPABASE_*）
   - 要么用 R2（填写 R2_*）
   - 不要两种都填

2. **删除所有注释**：
   - 删除所有以 `#` 开头的行
   - 只保留实际的配置项

3. **确保格式正确**：
   - 每行一个配置项
   - `KEY=value` 格式，等号两边不要有空格
   - 值不要加引号（除非值本身包含特殊字符）

4. **保存文件**：
   - 使用 vi：按 `Esc`，输入 `:wq`，按 `Enter`
   - 使用 nano：按 `Ctrl + O`，按 `Enter`，按 `Ctrl + X`

---

## 🚀 快速开始（推荐 Supabase）

如果你还没有配置存储，我**强烈推荐使用 Supabase**，因为：

1. **最简单**：5分钟完成配置
2. **免费额度充足**：足够个人项目使用
3. **国内访问稳定**：相对其他方案更稳定

### 快速配置 Supabase

1. 访问：https://supabase.com
2. 使用 GitHub 登录
3. 创建项目（选择 Singapore 区域）
4. 创建 Storage bucket：`word-formatter-storage`
5. 获取 API Key（Settings → API → service_role key）
6. 填写到 .env 文件

---

## 📞 需要帮助？

如果遇到问题：
1. 检查配置信息是否正确
2. 确保没有多余的空格或引号
3. 确保至少配置了一种存储方案
4. 查看项目文档中的存储配置说明

---

**配置好 .env 文件后，继续运行部署脚本！** 🚀




