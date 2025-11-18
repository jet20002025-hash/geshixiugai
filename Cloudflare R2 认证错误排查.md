# Cloudflare R2 认证错误排查

## 🔍 错误信息

**错误提示**：`Unable to authenticate request`

这个错误通常出现在以下场景：
1. 在 Cloudflare Dashboard 中创建 R2 API Token 时
2. 在配置 R2 环境变量时
3. 在使用 R2 API Token 访问 R2 存储时

---

## ✅ 解决方案

### 场景 1：在 Cloudflare Dashboard 中创建 API Token 时出错

#### 可能原因：
1. **账号权限不足**
   - 你的账号可能没有 R2 的访问权限
   - 需要确保账号已启用 R2 服务

2. **API Token 权限配置错误**
   - Token 权限设置不正确
   - 没有选择正确的 Account 或 Zone

#### 解决步骤：

**步骤 1：检查 R2 服务是否已启用**

1. 登录 Cloudflare Dashboard：https://dash.cloudflare.com
2. 在左侧菜单找到 **"R2"**
3. 如果看到 "Get started" 或 "Enable R2"，点击启用
4. 阅读并同意服务条款
5. 完成 R2 服务的启用

**步骤 2：创建 API Token（正确方法）**

1. 在 R2 页面，点击 **"Manage R2 API Tokens"**
   - 或直接访问：https://dash.cloudflare.com/profile/api-tokens

2. 点击 **"Create API Token"**

3. 选择 **"Custom token"**（自定义 Token）

4. 填写 Token 信息：
   - **Token name**：`word-formatter-r2-token`
   - **Permissions**（权限）：
     - 点击 **"Add"**
     - **Account** → **Cloudflare R2** → **Edit**（编辑权限）
   - **Account Resources**（账号资源）：
     - 选择 **"Include"**
     - 在下拉菜单中选择你的账号（Account）
   - **Zone Resources**（域名资源）：
     - 选择 **"None"**（R2 不需要域名权限）

5. 点击 **"Continue to summary"**

6. 检查配置，确认：
   - ✅ Permissions: `Account - Cloudflare R2 - Edit`
   - ✅ Account Resources: `Include - [你的账号名]`
   - ✅ Zone Resources: `None`

7. 点击 **"Create Token"**

8. **立即复制保存**以下信息（只显示一次）：
   - **Access Key ID**：类似 `a1b2c3d4e5f6g7h8i9j0`
   - **Secret Access Key**：类似 `AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`
   - **Account ID**：在 R2 页面顶部可以看到

---

### 场景 2：在 Vercel 中配置环境变量后仍然出错

#### 可能原因：
1. **环境变量值错误**
   - Access Key ID 或 Secret Access Key 复制不完整
   - 包含了多余的空格或换行符

2. **环境变量未应用到所有环境**
   - 只配置了 Production，没有配置 Preview 和 Development

#### 解决步骤：

**步骤 1：检查环境变量格式**

在 Vercel Dashboard → Settings → Environment Variables 中：

1. 检查每个环境变量的值：
   - ✅ `R2_ACCOUNT_ID`：应该是纯数字或字母数字组合，**没有空格**
   - ✅ `R2_ACCESS_KEY_ID`：应该是纯字符串，**没有空格**
   - ✅ `R2_SECRET_ACCESS_KEY`：应该是纯字符串，**没有空格**
   - ✅ `R2_BUCKET_NAME`：应该是纯字符串，**没有空格**

2. **重新复制粘贴**（确保没有多余空格）：
   - 在 Cloudflare 中重新查看 API Token
   - 逐个字符检查，确保没有复制到空格或换行符
   - 在 Vercel 中重新输入

**步骤 2：确保环境变量应用到所有环境**

在 Vercel 中，每个环境变量都要选择：
- ✅ **All Environments**（Production, Preview, Development）

**步骤 3：重新部署**

修改环境变量后，需要重新部署才能生效：

1. 在 Vercel Dashboard → Deployments
2. 点击 **"Redeploy"** 或触发新的部署

---

### 场景 3：代码中使用 R2 时出错

#### 可能原因：
1. **环境变量未正确加载**
   - Vercel 环境变量未设置
   - 环境变量名称拼写错误

2. **R2 Bucket 不存在**
   - Bucket 名称错误
   - Bucket 未创建

#### 解决步骤：

**步骤 1：验证环境变量**

在 Vercel Dashboard → Settings → Environment Variables 中，确认以下变量都已设置：

```
R2_ACCOUNT_ID=你的Account ID
R2_ACCESS_KEY_ID=你的Access Key ID
R2_SECRET_ACCESS_KEY=你的Secret Access Key
R2_BUCKET_NAME=word-formatter-storage
```

**步骤 2：验证 R2 Bucket 是否存在**

1. 登录 Cloudflare Dashboard
2. 进入 R2 页面
3. 确认 Bucket 名称与 `R2_BUCKET_NAME` 一致
4. 如果不存在，创建 Bucket：
   - 点击 **"Create bucket"**
   - 输入名称：`word-formatter-storage`
   - 点击 **"Create bucket"**

**步骤 3：检查代码中的环境变量名称**

确认代码中使用的环境变量名称与 Vercel 中设置的一致：

```python
# backend/app/services/r2_storage.py
self.account_id = os.getenv('R2_ACCOUNT_ID')  # ✅ 正确
self.access_key_id = os.getenv('R2_ACCESS_KEY_ID')  # ✅ 正确
self.secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')  # ✅ 正确
self.bucket_name = os.getenv('R2_BUCKET_NAME', 'word-formatter-storage')  # ✅ 正确
```

---

## 🔧 常见错误和解决方法

### 错误 1：`InvalidAccessKeyId`

**原因**：Access Key ID 错误或不存在

**解决**：
1. 在 Cloudflare 中重新创建 API Token
2. 复制新的 Access Key ID
3. 在 Vercel 中更新 `R2_ACCESS_KEY_ID`

### 错误 2：`SignatureDoesNotMatch`

**原因**：Secret Access Key 错误

**解决**：
1. 在 Cloudflare 中重新创建 API Token
2. 复制新的 Secret Access Key
3. 在 Vercel 中更新 `R2_SECRET_ACCESS_KEY`
4. 确保没有多余的空格或换行符

### 错误 3：`NoSuchBucket`

**原因**：Bucket 不存在或名称错误

**解决**：
1. 在 Cloudflare R2 页面确认 Bucket 名称
2. 在 Vercel 中更新 `R2_BUCKET_NAME`，确保与 Cloudflare 中的名称完全一致

### 错误 4：`AccessDenied`

**原因**：API Token 权限不足

**解决**：
1. 在 Cloudflare 中删除旧的 API Token
2. 重新创建 API Token，确保权限设置为：
   - **Account** → **Cloudflare R2** → **Edit**
3. 确保 Account Resources 选择了正确的账号

---

## 📋 完整检查清单

在遇到认证错误时，按以下清单逐一检查：

- [ ] **R2 服务已启用**
  - 在 Cloudflare Dashboard → R2 页面确认已启用

- [ ] **API Token 已创建**
  - 在 Cloudflare Dashboard → Profile → API Tokens 中确认 Token 存在

- [ ] **API Token 权限正确**
  - Permissions: `Account - Cloudflare R2 - Edit`
  - Account Resources: `Include - [你的账号]`
  - Zone Resources: `None`

- [ ] **环境变量已设置**
  - `R2_ACCOUNT_ID` 已设置
  - `R2_ACCESS_KEY_ID` 已设置
  - `R2_SECRET_ACCESS_KEY` 已设置
  - `R2_BUCKET_NAME` 已设置

- [ ] **环境变量值正确**
  - 没有多余的空格或换行符
  - 值与 Cloudflare 中显示的一致

- [ ] **环境变量应用到所有环境**
  - 在 Vercel 中选择了 "All Environments"

- [ ] **R2 Bucket 已创建**
  - 在 Cloudflare R2 页面确认 Bucket 存在
  - Bucket 名称与 `R2_BUCKET_NAME` 一致

- [ ] **已重新部署**
  - 修改环境变量后，已触发新的部署

---

## 🆘 仍然无法解决？

如果按照以上步骤仍然无法解决，请：

1. **检查 Cloudflare 账号状态**
   - 确认账号没有被限制或暂停
   - 确认 R2 服务在你的地区可用

2. **重新创建所有配置**
   - 删除旧的 API Token
   - 删除旧的 R2 Bucket（如果数据不重要）
   - 重新创建 API Token
   - 重新创建 R2 Bucket
   - 在 Vercel 中重新配置所有环境变量

3. **查看详细错误日志**
   - 在 Vercel Dashboard → Deployments → 选择最新的部署 → Functions → 查看日志
   - 查找包含 "R2"、"boto3"、"S3" 的错误信息

4. **联系 Cloudflare 支持**
   - 如果问题持续，可能是 Cloudflare 账号或服务的问题
   - 访问：https://support.cloudflare.com/

---

## 📝 快速参考

### 正确的 API Token 配置

```
Token name: word-formatter-r2-token
Permissions: Account - Cloudflare R2 - Edit
Account Resources: Include - [你的账号]
Zone Resources: None
```

### 正确的环境变量配置

```
R2_ACCOUNT_ID=你的Account ID（纯字符串，无空格）
R2_ACCESS_KEY_ID=你的Access Key ID（纯字符串，无空格）
R2_SECRET_ACCESS_KEY=你的Secret Access Key（纯字符串，无空格）
R2_BUCKET_NAME=word-formatter-storage（纯字符串，无空格）
```

### 环境变量应用范围

```
All Environments (Production, Preview, Development)
```

