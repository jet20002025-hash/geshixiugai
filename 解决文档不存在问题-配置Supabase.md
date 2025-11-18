# 解决文档不存在问题 - 配置 Supabase Storage

## 🎯 问题

在 Vercel 上，文档上传后无法找到，出现"文档不存在"错误。

**原因**：Vercel Serverless Functions 是无状态的，`/tmp` 目录在函数实例之间不共享。

**解决方案**：使用 Supabase Storage 持久化存储。

---

## ✅ 快速配置（5 分钟）

### 步骤 1：注册 Supabase（2 分钟）

1. 访问：https://supabase.com
2. 点击 **"Start your project"**
3. 使用 **GitHub 登录**（推荐，最简单）
4. 创建新项目：
   - **Name**：`word-formatter`（任意名称）
   - **Database Password**：设置密码（**请保存好！**）
   - **Region**：选择 `Southeast Asia (Singapore)`（离中国最近）
5. 点击 **"Create new project"**
6. 等待项目创建完成（约 1-2 分钟）

---

### 步骤 2：创建 Storage Bucket（1 分钟）

1. 在 Supabase Dashboard 左侧菜单，点击 **"Storage"**
2. 点击 **"Create a new bucket"** 或 **"New bucket"**
3. 填写信息：
   - **Name**：`word-formatter-storage`
   - **Public bucket**：**取消勾选**（私有存储，更安全）
4. 点击 **"Create bucket"**

---

### 步骤 3：获取 API Key（1 分钟）

1. 在 Supabase Dashboard 左侧菜单，点击 **"Settings"**（齿轮图标）
2. 点击 **"API"**
3. 找到 **"service_role" `secret`** key
4. 点击 **"Reveal"** 显示完整 key
5. **立即复制保存**以下信息：
   - **Project URL**：类似 `https://xxxxxxxxxxxxx.supabase.co`
   - **`service_role` `secret` key**：长字符串（只显示一次！）

---

### 步骤 4：配置 Vercel 环境变量（1 分钟）

1. 登录 Vercel Dashboard：https://vercel.com/dashboard
2. 选择你的项目：`geshixiugai`
3. 点击 **Settings** → **Environment Variables**
4. 依次添加以下环境变量：

#### 变量 1：SUPABASE_URL
- **Key**：`SUPABASE_URL`
- **Value**：你的 Project URL（如 `https://xxxxxxxxxxxxx.supabase.co`）
- **Environment**：选择 **All Environments**
- 点击 **"Save"**

#### 变量 2：SUPABASE_KEY
- **Key**：`SUPABASE_KEY`
- **Value**：你的 `service_role` secret key
- **Environment**：选择 **All Environments**
- 点击 **"Save"**

#### 变量 3：SUPABASE_BUCKET
- **Key**：`SUPABASE_BUCKET`
- **Value**：`word-formatter-storage`
- **Environment**：选择 **All Environments**
- 点击 **"Save"**

---

### 步骤 5：重新部署（1 分钟）

1. 在 Vercel Dashboard → **Deployments**
2. 点击最新的部署右侧的 **"..."** → **"Redeploy"**
3. 等待部署完成（约 1-2 分钟）

---

## ✅ 验证配置

部署完成后：

1. **查看 Vercel 日志**：
   - 在 Vercel Dashboard → Deployments → 选择最新部署 → Functions → Logs
   - 应该看到：`[Storage] Using Supabase Storage`

2. **测试上传文档**：
   - 访问你的网站
   - 上传一个文档
   - 应该可以正常处理，不再出现"文档不存在"错误

---

## 🔍 如果遇到问题

### 问题 1：看不到 `[Storage] Using Supabase Storage` 日志

**检查**：
1. 环境变量是否正确设置
2. `SUPABASE_URL` 和 `SUPABASE_KEY` 是否正确
3. 是否选择了 "All Environments"

**解决**：
- 重新检查环境变量
- 确保 `service_role` key 是正确的（不是 `anon` key）

### 问题 2：仍然出现"文档不存在"

**检查**：
1. Vercel 日志中是否有存储相关的错误
2. Supabase Dashboard → Storage → `word-formatter-storage` 中是否有文件

**解决**：
- 查看 Vercel 日志中的错误信息
- 检查 Supabase Storage 权限设置

---

## 📊 免费额度

Supabase 免费计划包括：
- ✅ **1 GB 存储空间**
- ✅ **2 GB 出站流量/月**
- ✅ **50,000 次 API 请求/月**

**对于个人项目，这些额度通常足够使用！**

---

## 🎉 完成！

配置完成后，文档会保存在 Supabase Storage 中，不再出现"文档不存在"的问题。

**如果遇到问题，告诉我具体的错误信息，我会帮你解决！**

