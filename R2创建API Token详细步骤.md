# Cloudflare R2 创建 API Token 详细步骤

## 🎯 目标

创建 R2 API Token，用于在 Vercel 中访问 R2 存储。

---

## 📋 步骤 1：进入 API Tokens 页面

### 方法 1：从 R2 页面进入（推荐）

1. **在 R2 Dashboard 页面**（你当前所在的页面）
2. **查看右侧边栏**，找到 **"Account Details"** 部分
3. **找到 "API Tokens"** 这一行
4. **点击右侧的 "{} Manage" 按钮**
5. 会跳转到 API Tokens 管理页面

### 方法 2：直接访问

1. **直接访问**：https://dash.cloudflare.com/profile/api-tokens
2. 或点击右上角头像 → **"My Profile"** → **"API Tokens"**

---

## 📋 步骤 2：创建新的 API Token

1. **在 API Tokens 页面**，点击 **"Create API Token"** 按钮（通常在页面右上角或顶部）

2. **选择 Token 类型**：
   - 选择 **"Custom token"**（自定义 Token）
   - 不要选择预设的模板

---

## 📋 步骤 3：配置 Token 权限

### 3.1 填写基本信息

- **Token name**：输入 `word-formatter-r2-token`
  - 这是 Token 的名称，用于识别用途

### 3.2 设置权限（Permissions）

1. **点击 "Add" 或 "+" 按钮**添加权限

2. **选择权限类型**：
   - 在权限列表中，找到 **"Account"**
   - 展开 **"Account"**
   - 找到 **"Cloudflare R2"**
   - 展开 **"Cloudflare R2"**
   - **选择 "Edit"**（编辑权限）
   - 这允许 Token 读写 R2 存储

### 3.3 设置账号资源（Account Resources）

1. **在 "Account Resources" 部分**：
   - 选择 **"Include"**（包含）
   - 在下拉菜单中选择**你的账号**（通常只有一个）

### 3.4 设置域名资源（Zone Resources）

1. **在 "Zone Resources" 部分**：
   - 选择 **"None"**（不需要）
   - R2 存储不需要域名权限

---

## 📋 步骤 4：检查并创建

1. **点击 "Continue to summary"** 或 **"Next"** 按钮

2. **检查配置摘要**：
   - ✅ Token name: `word-formatter-r2-token`
   - ✅ Permissions: `Account - Cloudflare R2 - Edit`
   - ✅ Account Resources: `Include - [你的账号名]`
   - ✅ Zone Resources: `None`

3. **确认无误后，点击 "Create Token"**

---

## 📋 步骤 5：保存 Token 信息（重要！）

**⚠️ 重要：Token 信息只显示一次，请立即复制保存！**

创建成功后，你会看到：

### 5.1 Access Key ID

- **显示位置**：页面顶部或中间
- **格式**：类似 `a1b2c3d4e5f6g7h8i9j0`（20 个字符）
- **操作**：点击复制图标或选中文本复制

### 5.2 Secret Access Key

- **显示位置**：在 Access Key ID 下方
- **格式**：类似 `AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`（40 个字符）
- **操作**：点击复制图标或选中文本复制
- **注意**：这个密钥只显示一次，关闭页面后就看不到了！

### 5.3 Account ID

- **显示位置**：可能在 Token 信息中，或在 R2 Dashboard 右侧
- **格式**：类似 `5003936d05d7bc23217a0fdef979...`（32 个字符）
- **操作**：在 R2 Dashboard 右侧可以看到，点击复制图标

---

## 📋 步骤 6：保存到安全的地方

**立即保存以下信息**：

```
R2_ACCOUNT_ID = 5003936d05d7bc23217a0fdef979...（从 R2 Dashboard 右侧复制）
R2_ACCESS_KEY_ID = a1b2c3d4e5f6g7h8i9j0（从 Token 页面复制）
R2_SECRET_ACCESS_KEY = AbCdEfGhIjKlMnOpQrStUvWxYz1234567890（从 Token 页面复制）
```

**保存方式**：
- 复制到文本文件
- 或直接复制到 Vercel 环境变量（下一步会用到）

---

## 🎯 下一步：配置 Vercel 环境变量

保存好 Token 信息后，下一步是在 Vercel 中配置环境变量：

1. **登录 Vercel Dashboard**：https://vercel.com/dashboard
2. **选择项目**：`geshixiugai`
3. **Settings** → **Environment Variables**
4. **添加 4 个环境变量**（使用刚才保存的信息）

详细步骤请查看：`R2存储配置步骤.md` 的步骤 3

---

## 🆘 常见问题

### Q1: 找不到 "Create API Token" 按钮？

**A**: 
- 确认你在 API Tokens 页面：https://dash.cloudflare.com/profile/api-tokens
- 如果还是找不到，尝试刷新页面（F5）
- 检查浏览器是否阻止了某些元素

### Q2: 找不到 "Cloudflare R2" 权限？

**A**: 
- 确认你的账号已启用 R2 服务
- 在 R2 Dashboard 中确认能看到 R2 界面
- 如果找不到，可能需要先创建 R2 Bucket

### Q3: Token 创建后找不到 Secret Access Key？

**A**: 
- Secret Access Key 只显示一次
- 如果关闭了页面，需要删除旧 Token 重新创建
- 在 API Tokens 页面，找到你的 Token，点击删除，然后重新创建

### Q4: 如何查看已创建的 Token？

**A**: 
- 在 API Tokens 页面可以看到所有 Token
- 但 Secret Access Key 不会再次显示（安全考虑）
- 如果丢失，需要重新创建

---

## 📝 检查清单

创建 API Token 时，确认：

- [ ] 已进入 API Tokens 页面
- [ ] 点击了 "Create API Token"
- [ ] 选择了 "Custom token"
- [ ] Token name 填写为 `word-formatter-r2-token`
- [ ] Permissions 设置为 `Account - Cloudflare R2 - Edit`
- [ ] Account Resources 选择了你的账号
- [ ] Zone Resources 设置为 `None`
- [ ] 已点击 "Create Token"
- [ ] **已复制保存 Access Key ID**
- [ ] **已复制保存 Secret Access Key**
- [ ] **已复制保存 Account ID**（从 R2 Dashboard）

---

## 💡 提示

1. **Secret Access Key 只显示一次**，务必立即复制保存
2. **如果丢失 Secret Access Key**，需要删除 Token 重新创建
3. **Token 创建后**，可以在 API Tokens 页面看到，但 Secret 不会再次显示
4. **Account ID** 可以在 R2 Dashboard 右侧随时查看和复制

---

## 🎉 完成！

创建好 API Token 并保存好信息后，告诉我：
- ✅ 已创建 Token
- ✅ 已保存 Access Key ID
- ✅ 已保存 Secret Access Key
- ✅ 已保存 Account ID

然后我会指导你配置 Vercel 环境变量！

