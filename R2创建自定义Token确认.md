# R2 创建自定义 Token - 确认步骤

## ✅ 是的，点击 "开始使用" 按钮

你看到了"自定义令牌"页面，这是正确的位置！

---

## 📋 操作步骤

### 步骤 1：点击 "开始使用" 按钮

1. **点击蓝色的 "开始使用" 按钮**
2. 会进入 Token 创建表单页面

### 步骤 2：填写 Token 信息

进入表单后，填写以下信息：

#### 1. 令牌名称（Token Name）
- **填写**：`word-formatter-r2-token`

#### 2. 权限（Permissions）
- **第一个下拉菜单**：选择 `帐户`（Account）
- **第二个下拉菜单**：选择 `Workers R2 存储`（Workers R2 Storage）
- **第三个下拉菜单**：选择 `Edit`（编辑）

#### 3. 帐户资源（Account Resources）
- **第一个下拉菜单**：选择 `包括`（Include）
- **第二个下拉菜单**：选择你的账号（如 `Z522168878@outlook.com's Account`）

#### 4. 域名资源（Zone Resources）
- **选择**：`None`（不需要）

#### 5. 其他设置
- **客户端 IP 地址筛选**：不需要设置（保持默认）
- **TTL**：不需要设置（保持默认，永久有效）

### 步骤 3：创建 Token

1. **点击 "Continue to summary"** 或 **"继续"** 按钮
2. **检查配置摘要**：
   - ✅ Token name: `word-formatter-r2-token`
   - ✅ Permissions: `Account - Workers R2 存储 - Edit`
   - ✅ Account Resources: `Include - [你的账号]`
   - ✅ Zone Resources: `None`
3. **点击 "Create Token"** 或 **"创建令牌"**

### 步骤 4：保存 Token 信息（重要！）

创建成功后，会显示两个值：

1. **Access Key ID**：
   - 格式：通常 20 个字符
   - 类似：`a1b2c3d4e5f6g7h8i9j0`
   - **立即复制保存**

2. **Secret Access Key**：
   - 格式：通常 40 个字符
   - 类似：`AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`
   - **立即复制保存**（只显示一次！）

---

## 📋 还需要收集的信息

除了 Access Key ID 和 Secret Access Key，还需要：

### Account ID

1. **回到 R2 Dashboard**：https://dash.cloudflare.com
2. **点击左侧菜单 "R2 对象存储"**
3. **查看右侧边栏 "Account Details"**
4. **找到 "Account ID"**
5. **点击复制图标**，复制 Account ID
   - 格式：32 个字符，类似 `5003936d05d7bc23217a0fdef979a238`

---

## ✅ 收集齐 3 个值后

收集齐以下 3 个值后，告诉我：

1. ✅ **Account ID** = `你的 Account ID`
2. ✅ **Access Key ID** = `你的 Access Key ID`
3. ✅ **Secret Access Key** = `你的 Secret Access Key`

然后我会指导你配置 Vercel 环境变量！

---

## 💡 提示

- **Secret Access Key 只显示一次**，创建后立即复制保存
- **如果丢失了 Secret Access Key**，需要删除 Token 重新创建
- **Account ID 可以随时查看**，在 R2 Dashboard 右侧

**现在点击 "开始使用" 按钮，按照上面的步骤创建 Token！**

