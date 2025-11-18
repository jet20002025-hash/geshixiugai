# 从 R2 存储桶页面进入 API Tokens

## 🔍 当前位置

你现在在：`R2 对象存储 / word-formatter-storage` → "对象" 标签页

这是存储桶的文件管理页面，不是创建 API Token 的地方。

---

## ✅ 如何进入 API Tokens 页面

### 方法 1：从 R2 Dashboard 主页面进入（推荐）

1. **点击页面顶部的 "R2 对象存储"**（在 "word-formatter-storage" 前面）
   - 这会回到 R2 Dashboard 主页面

2. **查看右侧边栏 "Account Details" 部分**

3. **找到 "API Tokens" 这一行**

4. **点击右侧的 "{} Manage" 按钮**
   - 这会跳转到 R2 专用的 API Tokens 页面

### 方法 2：从左侧菜单进入

1. **查看左侧菜单**
2. **找到 "R2 对象存储"**
3. **点击 "R2 对象存储"**（不是展开，是点击主菜单项）
4. **这会回到 R2 Dashboard 主页面**
5. **然后按照方法 1 的步骤 2-4 操作**

### 方法 3：直接访问（如果找不到）

如果找不到 "Manage" 按钮，可以尝试：

1. **在浏览器地址栏**，当前 URL 可能是：
   ```
   https://dash.cloudflare.com/.../r2/buckets/word-formatter-storage
   ```

2. **修改 URL 为**：
   ```
   https://dash.cloudflare.com/profile/api-tokens
   ```

3. **或者访问**：
   ```
   https://dash.cloudflare.com/profile/api-tokens
   ```

---

## 📋 进入 API Tokens 页面后

1. **点击 "Create API Token"** 或 **"创建 API 令牌"**

2. **选择 "Custom token"**（自定义令牌）

3. **配置权限**：
   - 第一个下拉菜单：`帐户`（Account）
   - 第二个下拉菜单：`Workers R2 存储`（Workers R2 Storage）
   - 第三个下拉菜单：`Edit`（编辑）

4. **填写 Token 名称**：`word-formatter-r2-token`

5. **配置账号资源**：
   - 选择 "Include"（包括）
   - 选择你的账号

6. **配置域名资源**：选择 "None"（不需要）

7. **点击 "Create Token"**

8. **立即复制保存两个值**：
   - **Access Key ID**
   - **Secret Access Key**（只显示一次！）

---

## 🎯 当前页面说明

你现在看到的页面是：
- **存储桶的文件管理页面**
- **用于上传/下载文件**
- **不是创建 API Token 的地方**

**需要先回到 R2 Dashboard 主页面，然后找到 API Tokens 入口。**

---

## 💡 提示

- **R2 Dashboard 主页面**：显示所有存储桶的列表
- **存储桶详情页面**：显示单个存储桶的文件和设置
- **API Tokens 页面**：创建和管理 API Token

**你现在在存储桶详情页面，需要回到 R2 Dashboard 主页面才能找到 API Tokens 入口。**

---

## 🆘 如果还是找不到

告诉我：
1. 你点击 "R2 对象存储" 后看到了什么？
2. 右侧边栏是否有 "Account Details" 部分？
3. 是否有 "API Tokens" 选项？

**或者直接访问**：https://dash.cloudflare.com/profile/api-tokens

**然后告诉我你看到了什么，我会继续指导你！**

