# Supabase Storage 配置步骤

## 📋 为什么选择 Supabase Storage？

- ✅ **免费额度充足**：1 GB 存储，2 GB 流量/月
- ✅ **国内可访问**（相对稳定）
- ✅ **简单易用**，API 友好
- ✅ **不需要信用卡**
- ✅ **与 Vercel 集成良好**

---

## 🚀 步骤 1：注册 Supabase 账号

### 1.1 访问 Supabase 官网

1. 访问：https://supabase.com
2. 点击右上角 **"Start your project"** 或 **"Sign in"**

### 1.2 选择登录方式

**推荐使用 GitHub 登录**（最简单）：
1. 点击 **"Continue with GitHub"**
2. 授权 Supabase 访问你的 GitHub 账号
3. 完成登录

**或者使用邮箱注册**：
1. 输入邮箱地址
2. 设置密码
3. 验证邮箱

---

## 📦 步骤 2：创建项目

### 2.1 创建新项目

1. 登录后，点击 **"New Project"**
2. 填写项目信息：
   - **Name**：`word-formatter`（或任意名称）
   - **Database Password**：设置数据库密码（**请保存好！**）
   - **Region**：选择离你最近的区域（如 `Southeast Asia (Singapore)`）
3. 点击 **"Create new project"**
4. 等待项目创建完成（约 1-2 分钟）

---

## 🗂️ 步骤 3：创建 Storage Bucket

### 3.1 进入 Storage 页面

1. 在左侧菜单找到 **"Storage"**，点击进入
2. 如果第一次使用，会看到欢迎页面

### 3.2 创建 Bucket

1. 点击 **"Create a new bucket"** 或 **"New bucket"**
2. 填写信息：
   - **Name**：`word-formatter-storage`
   - **Public bucket**：**取消勾选**（私有存储，更安全）
3. 点击 **"Create bucket"**

### 3.3 配置 Bucket 策略（可选）

如果需要公开访问文件，可以配置策略：
1. 点击 Bucket 名称进入详情
2. 在 **"Policies"** 标签页配置访问策略
3. 对于私有存储，可以跳过这一步

---

## 🔑 步骤 4：获取 API Key

### 4.1 进入 API 设置

1. 在左侧菜单找到 **"Settings"**（齿轮图标）
2. 点击 **"API"**

### 4.2 复制 API Key

你会看到两个 Key：
- **`anon` `public`**：用于客户端（前端）
- **`service_role` `secret`**：用于服务端（后端）**⚠️ 保密！**

**我们需要的是 `service_role` key**（用于服务端上传/下载文件）

1. 找到 **"service_role" `secret`** key
2. 点击 **"Reveal"** 显示完整 key
3. **立即复制保存**（只显示一次）

### 4.3 复制项目 URL

在同一个页面，你会看到：
- **Project URL**：类似 `https://xxxxxxxxxxxxx.supabase.co`

**复制这个 URL**，我们稍后会用到。

---

## ⚙️ 步骤 5：在 Vercel 配置环境变量

### 5.1 进入 Vercel 项目设置

1. 登录 Vercel Dashboard：https://vercel.com/dashboard
2. 选择你的项目：`geshixiugai`
3. 点击 **Settings** → **Environment Variables**

### 5.2 添加环境变量

依次添加以下环境变量：

#### 变量 1：SUPABASE_URL
- **Key**：`SUPABASE_URL`
- **Value**：你的 Project URL（如 `https://xxxxxxxxxxxxx.supabase.co`）
- **Environment**：选择 **All Environments**（Production, Preview, Development）
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

## ✅ 步骤 6：验证配置

### 6.1 检查环境变量

在 Vercel Dashboard → Settings → Environment Variables 中，确认以下变量都已设置：

```
✅ SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
✅ SUPABASE_KEY=你的service_role key
✅ SUPABASE_BUCKET=word-formatter-storage
```

### 6.2 重新部署

修改环境变量后，需要重新部署才能生效：

1. 在 Vercel Dashboard → Deployments
2. 点击最新的部署右侧的 **"..."** → **"Redeploy"**
3. 等待部署完成（约 1-2 分钟）

---

## 🧪 步骤 7：测试存储功能

部署完成后，测试文件上传和下载：

1. 访问你的网站：https://geshixiugai.org
2. 上传一个文档
3. 检查是否成功保存到 Supabase Storage

**如果成功**：
- 在 Supabase Dashboard → Storage → `word-formatter-storage` 中可以看到上传的文件

**如果失败**：
- 检查 Vercel 日志，查看错误信息
- 确认环境变量是否正确设置

---

## 🔒 安全注意事项

1. **不要泄露 `service_role` key**
   - 这个 key 有完整权限，可以访问所有数据
   - 只在服务端（Vercel）使用
   - 不要提交到 Git

2. **Bucket 设置为私有**
   - 创建 Bucket 时取消勾选 "Public bucket"
   - 文件只能通过 API 访问，更安全

3. **定期检查访问日志**
   - 在 Supabase Dashboard → Logs 中查看访问记录
   - 发现异常访问及时处理

---

## 📊 免费额度说明

Supabase 免费计划包括：
- ✅ **1 GB 存储空间**
- ✅ **2 GB 出站流量/月**
- ✅ **50,000 次 API 请求/月**

**对于个人项目，这些额度通常足够使用！**

如果超出免费额度，Supabase 会：
- 提前通知你
- 可以升级到付费计划（$25/月）

---

## 🆘 常见问题

### Q1: 找不到 `service_role` key？

**A**: 
- 在 Settings → API 页面
- 找到 **"service_role" `secret`** 部分
- 点击 **"Reveal"** 显示完整 key

### Q2: 上传文件失败？

**A**: 检查以下几点：
1. 环境变量是否正确设置
2. Bucket 名称是否正确
3. `service_role` key 是否正确（不是 `anon` key）
4. 查看 Vercel 日志中的错误信息

### Q3: 如何查看已上传的文件？

**A**: 
1. 登录 Supabase Dashboard
2. 进入 Storage → `word-formatter-storage`
3. 可以看到所有上传的文件

### Q4: 文件可以公开访问吗？

**A**: 
- 如果 Bucket 设置为私有，需要通过 API 访问
- 如果需要公开访问，可以：
  1. 将 Bucket 设置为 Public
  2. 或配置 Bucket 策略允许公开读取

---

## 📝 下一步

配置完成后，代码会自动使用 Supabase Storage。

**如果遇到问题，告诉我具体的错误信息，我会帮你解决！**

