# R2 Token 类型说明

## 🔍 重要区别

你看到了两种不同的 Token/Key，它们用途不同：

---

## ❌ 不需要的 Key

### 1. Global API Key（全局 API 密钥）
- **位置**：My Profile → API Keys
- **用途**：用于访问 Cloudflare 的通用 API
- **我们不需要**：这个不是用于 R2 存储的

### 2. Origin CA Key（源站 CA 密钥）
- **位置**：My Profile → API Keys
- **用途**：用于 Origin CA 证书
- **我们不需要**：这个也不是用于 R2 存储的

---

## ✅ 我们需要的：R2 API Token

### R2 存储需要的是：Access Key ID 和 Secret Access Key

这些是通过 **"Manage R2 API Tokens"** 创建的，不是普通的 API Token。

---

## 🎯 正确的创建方式

### 方法 1：从 R2 Dashboard 进入（推荐）

1. **回到 R2 Dashboard**：https://dash.cloudflare.com
2. **点击左侧菜单 "R2 对象存储"**
3. **查看右侧边栏 "Account Details"**
4. **找到 "API Tokens"**
5. **点击 "{} Manage" 按钮**
6. **这会跳转到 R2 专用的 API Tokens 页面**

### 方法 2：直接访问 R2 API Tokens

如果找不到 "Manage" 按钮，可以：

1. **在 R2 Dashboard 页面**
2. **查看页面顶部或底部**
3. **寻找 "Manage R2 API Tokens" 链接**

---

## 📋 R2 API Token 创建步骤

1. **进入 R2 API Tokens 页面**（不是普通的 API Tokens）

2. **创建 R2 API Token**：
   - 点击 "Create API Token" 或 "创建 API 令牌"
   - 选择 "Custom token"
   - 配置权限：Account → Workers R2 存储 → Edit
   - Token name：`word-formatter-r2-token`
   - Account Resources：Include → 选择你的账号
   - Zone Resources：None

3. **创建成功后，会显示两个值**：
   - **Access Key ID**：类似 `a1b2c3d4e5f6g7h8i9j0`（20 个字符）
   - **Secret Access Key**：类似 `AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`（40 个字符）

---

## 🔍 如何区分

### 普通 API Token
- 显示格式：类似 `Ko5KggB-WuzqgTR-kcUIWVOSOY6NpofvaMTdIsWF`
- 只有一个值
- 用于访问 Cloudflare API

### R2 API Token（我们需要的）
- 显示格式：两个值
  - Access Key ID（20 个字符）
  - Secret Access Key（40 个字符）
- 用于访问 R2 存储

---

## 🎯 下一步操作

### 如果你创建的是普通 API Token

1. **需要找到 R2 专用的 API Tokens 页面**
2. **从 R2 Dashboard 进入**：
   - 在 R2 Dashboard 右侧找到 "API Tokens"
   - 点击 "{} Manage" 按钮

### 如果你已经创建了 R2 API Token

1. **确认你看到了两个值**：
   - Access Key ID
   - Secret Access Key

2. **立即复制保存这两个值**

3. **还需要 Account ID**：
   - 在 R2 Dashboard 右侧 "Account Details" 中
   - 点击复制图标复制

---

## 📝 总结

- ❌ **Global API Key**：不需要
- ❌ **Origin CA Key**：不需要
- ❌ **普通 API Token**：不需要
- ✅ **R2 API Token**（Access Key ID + Secret Access Key）：**这个才是我们需要的！**

---

## 🆘 如果找不到 R2 API Tokens 页面

告诉我：
1. 你在哪个页面？
2. 看到了什么选项？
3. 是否有 "Manage R2 API Tokens" 或类似的链接？

我会进一步指导你！

