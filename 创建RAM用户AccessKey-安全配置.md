# 创建 RAM 用户 AccessKey - 安全配置指南

## 🎯 为什么使用 RAM 用户 AccessKey？

阿里云推荐使用 **RAM 用户 AccessKey**，而不是云账号 AccessKey，因为：

- ✅ **更安全**：权限最小化，只授予必要的 OSS 权限
- ✅ **风险可控**：即使泄露，也不会影响整个账号
- ✅ **便于管理**：可以随时撤销或更换 AccessKey

---

## 📋 创建 RAM 用户 AccessKey 步骤

### 步骤 1：创建 RAM 用户

1. **登录 RAM 控制台**
   - 访问：https://ram.console.aliyun.com/
   - 或从阿里云控制台 → 访问控制（RAM）

2. **创建用户**
   - 点击左侧菜单 **"用户"**
   - 点击 **"创建用户"**
   - 填写信息：
     - **登录名称**：`geshixiugai-oss-user`（或你喜欢的名称）
     - **显示名称**：`格式修改器OSS用户`（可选）
     - **访问方式**：勾选 **"编程访问"**（用于 AccessKey）
   - 点击 **"确定"**

### 步骤 2：为 RAM 用户授权 OSS 权限

1. **找到刚创建的用户**
   - 在用户列表中，找到你刚创建的用户
   - 点击用户名进入详情

2. **添加权限**
   - 点击 **"添加权限"**
   - 选择 **"AliyunOSSFullAccess"**（OSS 完全访问权限）
   - 或选择自定义策略，只授予特定 Bucket 的权限（更安全）

3. **确认授权**
   - 点击 **"确定"** 完成授权

### 步骤 3：创建 AccessKey

1. **返回用户列表**
   - 找到你的 RAM 用户
   - 点击 **"创建 AccessKey"**

2. **确认安全提示**
   - 阅读安全提示
   - 勾选 **"我确认知晓 AccessKey 安全风险"**
   - 点击 **"使用 RAM 用户 AccessKey"**（蓝色按钮）

3. **保存 AccessKey**
   - **立即复制保存**（只显示一次）：
     - **AccessKey ID** → `OSS_ACCESS_KEY_ID`
     - **AccessKey Secret** → `OSS_ACCESS_KEY_SECRET`

---

## 🔒 更安全的权限配置（可选）

如果你想要更精细的权限控制，可以创建自定义策略：

### 创建自定义策略

1. **进入策略管理**
   - RAM 控制台 → 策略管理 → 创建策略

2. **选择脚本配置**
   - 选择 **"脚本配置"**
   - 填写策略名称：`geshixiugai-oss-policy`

3. **配置策略内容**

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "oss:PutObject",
        "oss:GetObject",
        "oss:DeleteObject",
        "oss:ListObjects",
        "oss:HeadObject"
      ],
      "Resource": [
        "acs:oss:*:*:word-formatter-storage",
        "acs:oss:*:*:word-formatter-storage/*"
      ]
    }
  ]
}
```

4. **授权给 RAM 用户**
   - 在用户详情页 → 添加权限
   - 选择你刚创建的自定义策略

---

## ✅ 使用 RAM 用户 AccessKey

创建完成后，使用 RAM 用户的 AccessKey 填写到 `.env` 文件：

```bash
OSS_ACCESS_KEY_ID=RAM用户的AccessKey ID
OSS_ACCESS_KEY_SECRET=RAM用户的AccessKey Secret
OSS_BUCKET_NAME=word-formatter-storage
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_REGION=cn-hangzhou
```

---

## 📝 完整操作流程

```
1. 访问 RAM 控制台
   ↓
2. 创建 RAM 用户（勾选"编程访问"）
   ↓
3. 为用户授权 OSS 权限
   ↓
4. 创建 AccessKey
   ↓
5. 保存 AccessKey ID 和 Secret
   ↓
6. 填写到 .env 文件
```

---

## ⚠️ 安全提示

1. **妥善保管 AccessKey**：
   - 不要提交到代码仓库
   - 不要分享给他人
   - 定期更换（建议每 3-6 个月）

2. **最小化权限**：
   - 只授予必要的 OSS 权限
   - 不要授予其他云服务的权限

3. **监控使用**：
   - 定期查看 OSS 访问日志
   - 发现异常及时更换 AccessKey

---

## 🎉 优势总结

使用 RAM 用户 AccessKey：
- ✅ 更安全：权限最小化
- ✅ 风险可控：不影响主账号
- ✅ 便于管理：可以随时撤销

**推荐：选择"使用 RAM 用户 AccessKey"！** 🔒










