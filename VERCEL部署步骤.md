# Vercel 部署步骤 - 详细指南

## 方法1: 通过 GitHub 自动部署（推荐 ⭐）

### 第一步：准备 GitHub 仓库

1. **创建 GitHub 仓库**（如果还没有）
   ```bash
   # 在本地执行
   cd /Users/zwj/word格式修改器
   
   # 如果还没有 git 仓库，初始化
   git init
   git add .
   git commit -m "Initial commit"
   
   # 在 GitHub 创建新仓库，然后连接
   git remote add origin https://github.com/你的用户名/word-formatter.git
   git push -u origin main
   ```

2. **或者使用现有仓库**
   - 确保代码已推送到 GitHub

### 第二步：在 Vercel 导入项目

1. **登录 Vercel Dashboard**
   - 访问 https://vercel.com/dashboard
   - 确保已登录

2. **创建新项目**
   - 点击右上角 **"Add New..."** → **"Project"**
   - 或者点击 **"Import Project"**

3. **导入 GitHub 仓库**
   - 选择 **"Import Git Repository"**
   - 选择你的 GitHub 仓库（word-formatter 或你的仓库名）
   - 点击 **"Import"**

4. **配置项目设置**
   - **Framework Preset**: 选择 **"Other"** 或 **"Other (no framework)"**
   - **Root Directory**: 保持默认 `./`（项目根目录）
   - **Build Command**: 留空（不需要构建）
   - **Output Directory**: 留空
   - **Install Command**: `pip install -r requirements.txt`
   - **Python Version**: 选择 `3.12`（如果可用）

5. **添加环境变量**（重要！）
   点击 **"Environment Variables"**，添加以下变量：
   
   ```
   R2_ACCOUNT_ID=你的Account ID
   R2_ACCESS_KEY_ID=你的Access Key ID
   R2_SECRET_ACCESS_KEY=你的Secret Access Key
   R2_BUCKET_NAME=word-formatter-storage
   R2_ENDPOINT=https://你的Account ID.r2.cloudflarestorage.com
   ```
   
   **注意**: 
   - 如果还没有 R2，可以先不添加这些变量（代码会使用本地存储）
   - 每个变量都要添加，然后选择环境：Production, Preview, Development

6. **部署**
   - 点击 **"Deploy"**
   - 等待部署完成（约 2-3 分钟）

---

## 方法2: 使用 Vercel CLI（命令行）

### 第一步：安装 Vercel CLI

```bash
# 安装 Vercel CLI
npm install -g vercel
```

### 第二步：登录 Vercel

```bash
# 登录（会打开浏览器）
vercel login
```

### 第三步：部署项目

```bash
# 进入项目目录
cd /Users/zwj/word格式修改器

# 首次部署（会引导配置）
vercel

# 按照提示操作：
# - Set up and deploy? Yes
# - Which scope? 选择你的账户
# - Link to existing project? No（首次部署）
# - Project name? word-formatter（或你喜欢的名字）
# - Directory? ./
# - Override settings? No

# 部署到生产环境
vercel --prod
```

### 第四步：配置环境变量（CLI 方式）

```bash
# 添加环境变量
vercel env add R2_ACCOUNT_ID
vercel env add R2_ACCESS_KEY_ID
vercel env add R2_SECRET_ACCESS_KEY
vercel env add R2_BUCKET_NAME
vercel env add R2_ENDPOINT

# 每次添加时会提示输入值
# 选择环境：Production, Preview, Development（全选）
```

---

## 部署后验证

### 1. 检查部署状态

在 Vercel Dashboard 中：
- 查看 **Deployments** 标签
- 应该看到部署状态为 **"Ready"**（绿色）

### 2. 测试访问

部署完成后，Vercel 会提供一个 URL，类似：
- `https://word-formatter-xxx.vercel.app`

访问这个 URL：
- ✅ 应该看到健康检查：`{"status":"ok"}`
- ✅ API 文档：`https://word-formatter-xxx.vercel.app/docs`
- ✅ 前端页面：`https://word-formatter-xxx.vercel.app/web`

### 3. 添加自定义域名

1. 在 Vercel 项目设置中
2. 点击 **Settings** → **Domains**
3. 点击 **Add Domain**
4. 输入：`geshixiugai.org`
5. 点击 **Add**
6. Vercel 会自动验证域名

---

## 常见问题

### Q1: 部署失败怎么办？

**检查：**
1. `requirements.txt` 是否正确
2. `vercel.json` 配置是否正确
3. `api/index.py` 是否存在
4. 查看 Vercel 部署日志中的错误信息

### Q2: 找不到 api/index.py？

**解决：**
- 确保 `api/index.py` 文件存在
- 检查文件路径是否正确

### Q3: 环境变量在哪里添加？

**方法1（推荐）**: Dashboard
- 项目设置 → Environment Variables → Add

**方法2**: CLI
- 使用 `vercel env add` 命令

### Q4: 部署后访问 404？

**检查：**
1. `vercel.json` 路由配置是否正确
2. `api/index.py` 是否正确导出 app
3. 查看 Vercel 函数日志

---

## 下一步

部署成功后：
1. ✅ 测试 API 是否正常工作
2. ✅ 配置自定义域名（geshixiugai.org）
3. ✅ 配置 Cloudflare DNS（参考之前的指南）
4. ✅ 测试文件上传功能

---

## 需要帮助？

如果遇到问题：
1. 查看 Vercel 部署日志
2. 检查代码是否有语法错误
3. 确认所有文件都已提交到 GitHub

