# Vercel 存储问题解决方案

## 🔍 问题确认

错误信息：`文档不存在: c687d882ec93433898accbc63d5f68e9`

**问题根源**：
- Vercel Serverless Functions 是无状态的
- 文档保存在 `/tmp` 目录，但 `/tmp` 目录在函数实例之间**不共享**
- 文档上传时保存在一个实例的 `/tmp` 目录
- 支付时在另一个实例上，找不到文件

---

## ✅ 解决方案：使用 Cloudflare R2 持久化存储

### 步骤 1：创建 Cloudflare R2 Bucket

1. **登录 Cloudflare Dashboard**
   - 访问：https://dash.cloudflare.com
   - 登录你的账号

2. **创建 R2 Bucket**
   - 点击左侧菜单 "R2"
   - 点击 "Create bucket"
   - 输入 bucket 名称：`word-formatter-storage`
   - 点击 "Create bucket"

3. **创建 API Token**
   - 在 R2 页面，点击 "Manage R2 API Tokens"
   - 点击 "Create API Token"
   - 设置权限：**Object Read & Write**
   - 点击 "Create API Token"
   - **立即复制保存**以下信息（只显示一次）：
     - `Account ID`
     - `Access Key ID`
     - `Secret Access Key`

---

### 步骤 2：配置 Vercel 环境变量

在 Vercel Dashboard → 项目设置 → Environment Variables 中添加：

```
R2_ACCOUNT_ID=你的Account ID
R2_ACCESS_KEY_ID=你的Access Key ID
R2_SECRET_ACCESS_KEY=你的Secret Access Key
R2_BUCKET_NAME=word-formatter-storage
```

**注意**：
- `R2_ENDPOINT` 不需要单独设置，代码会自动构建
- 所有环境变量选择 "All Environments"（Production, Preview, Development）

---

### 步骤 3：修改代码使用 R2 存储

我已经准备好了 R2 存储类（`backend/app/services/r2_storage.py`），但需要修改 `DocumentService` 使用它。

**需要修改的文件**：
- `backend/app/services/document_service.py` - 使用 R2 存储替代本地文件系统

---

## 🚀 快速修复方案（临时）

如果你现在需要立即使用，可以：

### 方案 A：在同一会话中快速支付

1. 上传文档后，**立即**点击支付（不要等待）
2. 可能使用同一个函数实例，文件还在 `/tmp` 目录中

### 方案 B：查看 Vercel 日志确认问题

1. 登录 Vercel Dashboard
2. 进入你的项目 → **Functions** → **Logs**
3. 查找以下日志：
   - `[Mock Payment API]` 开头的日志
   - `[PaymentService]` 开头的日志
   - 查看 `DOCUMENT_DIR` 的路径
   - 查看所有文档目录列表

4. **告诉我日志内容**，我会帮你进一步分析

---

## 📋 检查清单

完成以下步骤：

- [ ] 创建 Cloudflare R2 Bucket
- [ ] 创建 R2 API Token
- [ ] 在 Vercel 配置环境变量
- [ ] 修改代码使用 R2 存储
- [ ] 重新部署
- [ ] 测试支付功能

---

## 💡 为什么需要 R2 存储？

**Vercel Serverless Functions 的限制**：
- ❌ `/tmp` 目录在函数实例之间不共享
- ❌ 文件在函数执行结束后可能被清理
- ❌ 无法保证文件持久化

**R2 存储的优势**：
- ✅ 文件持久化存储
- ✅ 所有函数实例都可以访问
- ✅ 免费额度充足（10GB 存储，1000 万次读取/月）
- ✅ 与 Cloudflare CDN 集成

---

## 🎯 下一步

**选择 1：立即配置 R2 存储（推荐）**
- 我会帮你修改代码使用 R2 存储
- 配置完成后，问题会彻底解决

**选择 2：先查看日志**
- 查看 Vercel 日志，确认问题
- 然后决定是否需要 R2 存储

**告诉我你的选择，我会帮你完成！**

