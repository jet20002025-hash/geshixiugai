# RAM 快速开始操作步骤

## 🎯 当前页面说明

你看到的是 RAM 快速开始页面，用于创建"用于程序访问的超级用户"。

---

## ⚠️ 重要提示

**快速开始创建的超级用户权限较大**，如果你想要更精细的权限控制，建议：

1. **方案 A（推荐）**：先完成快速开始，然后修改权限为只授予 OSS 权限
2. **方案 B**：退出快速开始，手动创建用户（见下方"手动创建"部分）

---

## 📋 方案 A：使用快速开始（简单快速）

### 步骤 1：确认用户信息

1. **登录名称**：
   - 已经预填：`power-application-user`
   - 可以保持默认，或改为：`geshixiugai-oss-user`

2. **访问方式**：
   - ✅ **API 访问**：已勾选（必须勾选）
   - ❌ **控制台访问**：未勾选（正确，程序访问不需要）

### 步骤 2：选择权限策略

1. **权限策略**部分：
   - 当前选择：`PowerUserAccess`（系统策略）
   - 这个策略权限较大，但可以先使用

2. **点击"确定"或"创建"按钮**

### 步骤 3：保存 AccessKey

创建完成后，会显示 AccessKey：
- **立即复制保存**（只显示一次）：
  - **AccessKey ID** → `OSS_ACCESS_KEY_ID`
  - **AccessKey Secret** → `OSS_ACCESS_KEY_SECRET`

### 步骤 4：（可选）修改权限为仅 OSS

如果你想要更精细的权限控制：

1. **进入用户管理**
   - RAM 控制台 → 用户 → 找到刚创建的用户

2. **修改权限**
   - 点击用户名进入详情
   - 点击"权限"标签
   - 移除 `PowerUserAccess` 策略
   - 添加 `AliyunOSSFullAccess` 策略（只授予 OSS 权限）

---

## 📋 方案 B：手动创建用户（更精细控制）

如果你想跳过快速开始，手动创建：

### 步骤 1：退出快速开始

- 点击左侧菜单 **"用户"**
- 点击 **"创建用户"**

### 步骤 2：填写用户信息

1. **登录名称**：`geshixiugai-oss-user`
2. **显示名称**：`格式修改器OSS用户`（可选）
3. **访问方式**：
   - ✅ 勾选 **"API 访问"**
   - ❌ 不勾选 **"控制台访问"**
4. 点击 **"确定"**

### 步骤 3：授权 OSS 权限

1. **添加权限**
   - 在用户详情页，点击 **"添加权限"**
   - 选择 **"AliyunOSSFullAccess"**（OSS 完全访问权限）
   - 点击 **"确定"**

### 步骤 4：创建 AccessKey

1. **创建 AccessKey**
   - 在用户详情页，点击 **"创建 AccessKey"**
   - 确认安全提示
   - 点击 **"使用 RAM 用户 AccessKey"**

2. **保存 AccessKey**
   - 立即复制保存 AccessKey ID 和 Secret

---

## ✅ 推荐操作流程

### 如果你想要快速开始：

1. ✅ 保持"API 访问"勾选
2. ✅ 保持"控制台访问"不勾选
3. ✅ 保持默认的权限策略（PowerUserAccess）
4. ✅ 点击"确定"创建
5. ✅ 保存 AccessKey ID 和 Secret

### 如果你想要更精细的权限：

1. 点击左侧菜单 **"用户"**，退出快速开始
2. 按照"方案 B：手动创建用户"操作
3. 只授予 OSS 权限

---

## 📝 填写到 .env 文件

创建完成后，在服务器上填写：

```bash
cd /var/www/geshixiugai
vi .env
```

填入：

```bash
OSS_ACCESS_KEY_ID=你的AccessKey ID
OSS_ACCESS_KEY_SECRET=你的AccessKey Secret
OSS_BUCKET_NAME=word-formatter-storage
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_REGION=cn-hangzhou
```

---

## 💡 建议

**对于快速部署**：
- 使用快速开始（方案 A）
- 先完成部署
- 后续可以再优化权限

**对于生产环境**：
- 使用手动创建（方案 B）
- 只授予必要的 OSS 权限
- 更安全

---

**现在你可以：**
1. 直接点击"确定"完成快速开始（简单快速）
2. 或点击左侧"用户"手动创建（更精细控制）

选择哪种方式都可以，告诉我你的选择！🚀


