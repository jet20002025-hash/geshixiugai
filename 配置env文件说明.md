# 配置 .env 文件说明

## 📋 当前状态

部署脚本已创建 `.env` 文件模板，现在需要填入实际的配置信息。

---

## 🚀 快速配置步骤

### 在服务器上执行（阿里云控制台的对话框里）

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 编辑 .env 文件
nano .env
```

### 在 nano 编辑器中：

1. **使用方向键移动光标**
2. **删除示例内容，填入实际配置**
3. **保存**：按 `Ctrl + O`，然后按 `Enter`
4. **退出**：按 `Ctrl + X`

---

## 📝 .env 文件配置示例

### 如果使用 Supabase Storage（推荐）

```bash
SUPABASE_URL=https://你的项目ID.supabase.co
SUPABASE_KEY=你的service_role key
SUPABASE_BUCKET=word-formatter-storage
```

### 如果使用 Cloudflare R2

```bash
R2_ACCOUNT_ID=你的Account ID
R2_ACCESS_KEY_ID=你的Access Key ID
R2_SECRET_ACCESS_KEY=你的Secret Access Key
R2_BUCKET_NAME=word-formatter-storage
R2_ENDPOINT=https://你的Account ID.r2.cloudflarestorage.com
```

### 如果使用 Backblaze B2

```bash
B2_ACCOUNT_ID=你的Account ID
B2_APPLICATION_KEY=你的Application Key
B2_BUCKET_NAME=word-formatter-storage
B2_ENDPOINT=https://s3.us-west-000.backblazeb2.com
```

### 支付配置（可选，如果有）

```bash
ALIPAY_APP_ID=你的支付宝AppID
ALIPAY_PRIVATE_KEY=你的支付宝私钥
ALIPAY_PUBLIC_KEY=支付宝公钥
```

---

## 💡 重要提示

1. **至少配置一种存储方案**（Supabase/R2/B2）
2. **不要包含注释符号**（`#` 开头的行会被忽略）
3. **确保没有多余的空格**
4. **私钥和密钥要完整复制，不要遗漏**

---

## ✅ 配置完成后

保存 `.env` 文件后，继续运行部署脚本，或者如果脚本已暂停，按 `Enter` 继续。

---

## 🔍 如何获取配置信息

### Supabase Storage

1. 登录 Supabase：https://supabase.com
2. 进入项目 → Settings → API
3. 复制：
   - **Project URL** → `SUPABASE_URL`
   - **service_role secret key** → `SUPABASE_KEY`
4. Storage → 创建 bucket → `SUPABASE_BUCKET`

### Cloudflare R2

1. 登录 Cloudflare Dashboard
2. R2 → Manage R2 API Tokens
3. 创建 Token，获取：
   - Account ID → `R2_ACCOUNT_ID`
   - Access Key ID → `R2_ACCESS_KEY_ID`
   - Secret Access Key → `R2_SECRET_ACCESS_KEY`
   - Endpoint URL → `R2_ENDPOINT`

---

**配置好 .env 文件后，继续部署流程！** 🚀










