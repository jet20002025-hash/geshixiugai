# 🚀 快速部署指南

## 5分钟快速上线

### 前置准备

1. **Cloudflare R2 存储**（免费）
   - 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
   - R2 → Create bucket → 创建 `word-formatter-storage`
   - R2 → Manage R2 API Tokens → Create API Token
   - 保存：`Account ID`、`Access Key ID`、`Secret Access Key`

2. **GitHub 仓库**
   - 将代码推送到 GitHub

### 部署步骤

#### 方法1: 通过 GitHub 自动部署（推荐 ⭐）

1. **连接 Vercel**
   - 访问 [vercel.com](https://vercel.com)
   - 使用 GitHub 账号登录
   - 点击 "New Project"
   - 导入你的 GitHub 仓库

2. **配置项目**
   - Framework Preset: **Other**
   - Root Directory: `./` (默认)
   - Build Command: 留空
   - Output Directory: 留空
   - Install Command: `pip install -r requirements.txt`

3. **添加环境变量**
   在 Vercel 项目设置 → Environment Variables 中添加：
   ```
   R2_ACCOUNT_ID=你的Account ID
   R2_ACCESS_KEY_ID=你的Access Key ID
   R2_SECRET_ACCESS_KEY=你的Secret Access Key
   R2_BUCKET_NAME=word-formatter-storage
   R2_ENDPOINT=https://你的Account ID.r2.cloudflarestorage.com
   ```

4. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约 2-3 分钟）

#### 方法2: 使用 Vercel CLI

```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 登录
vercel login

# 3. 部署
cd /Users/zwj/word格式修改器
vercel

# 4. 生产环境部署
vercel --prod
```

### 配置域名

1. **在 Vercel 添加域名**
   - 项目设置 → Domains → Add Domain
   - 输入你的域名（如：`formatter.example.com`）

2. **在 Cloudflare 配置 DNS**
   - 添加 CNAME 记录：
     - 名称：`@` 或 `www`
     - 目标：Vercel 提供的域名（如：`cname.vercel-dns.com`）

3. **等待 DNS 生效**（通常几分钟）

### 访问测试

部署完成后访问：
- 健康检查: `https://your-domain.vercel.app/`
- API 文档: `https://your-domain.vercel.app/docs`
- 前端页面: `https://your-domain.vercel.app/web`

## ⚠️ 重要提示

### 当前限制

1. **文件存储**: 代码已准备好 R2 存储，但需要修改 `document_service.py` 使用 R2 而不是本地文件系统
2. **执行时间**: Vercel 免费版 10 秒限制，处理大文档可能超时
3. **文件大小**: 上传文件限制 4.5MB（Vercel 限制）

### 后续优化建议

1. **异步处理**: 大文档处理改为异步任务
2. **直接上传**: 文件直接上传到 R2，不经过 Vercel
3. **队列系统**: 使用 Cloudflare Queues 处理长时间任务

## 🔧 故障排查

### 部署失败
- 检查 `requirements.txt` 是否正确
- 检查 Python 版本（Vercel 默认 3.9，需要 3.12 请在环境变量设置）

### 文件上传失败
- 检查 R2 环境变量是否正确
- 检查 R2 bucket 权限设置

### 国内访问慢
- 使用 Cloudflare CDN 加速
- 考虑使用国内 CDN（如又拍云）

## 📞 需要帮助？

查看详细文档：`部署说明.md`

