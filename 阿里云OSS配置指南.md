# 阿里云 OSS 配置指南

## 🎯 为什么选择阿里云 OSS？

如果你已经在使用阿里云服务器，**强烈推荐使用阿里云 OSS**：

- ✅ **同地域访问速度快**：服务器和存储在同一地域，访问速度最快
- ✅ **稳定可靠**：阿里云官方服务，稳定性和可靠性高
- ✅ **价格合理**：按量付费，成本可控
- ✅ **管理方便**：在同一个控制台管理服务器和存储

---

## 📋 配置步骤

### 步骤 1：登录阿里云控制台

1. 访问：https://oss.console.aliyun.com/
2. 使用你的阿里云账号登录

### 步骤 2：创建 OSS Bucket

1. 点击左侧菜单 **"Bucket 列表"**
2. 点击 **"创建 Bucket"**
3. 填写信息：
   - **Bucket 名称**：`word-formatter-storage`（或你喜欢的名称）
   - **地域**：选择与你的服务器相同的地域（如：华东1-杭州）
   - **存储类型**：标准存储（默认）
   - **读写权限**：私有（推荐，更安全）
   - **服务端加密**：可选
4. 点击 **"确定"** 创建

### 步骤 3：获取 AccessKey

1. 鼠标悬停在右上角头像上
2. 点击 **"AccessKey 管理"**
3. 如果还没有 AccessKey，点击 **"创建 AccessKey"**
4. **立即复制保存**（只显示一次）：
   - **AccessKey ID** → `OSS_ACCESS_KEY_ID`
   - **AccessKey Secret** → `OSS_ACCESS_KEY_SECRET`

**⚠️ 安全提示**：
- AccessKey Secret 只显示一次，请妥善保存
- 不要将 AccessKey 提交到代码仓库
- 建议创建子账号的 AccessKey，并只授予 OSS 相关权限

### 步骤 4：确定 Endpoint 和 Region

根据你创建 Bucket 时选择的地域，确定 Endpoint：

| 地域 | Region | Endpoint |
|------|--------|----------|
| 华东1（杭州） | cn-hangzhou | https://oss-cn-hangzhou.aliyuncs.com |
| 华东2（上海） | cn-shanghai | https://oss-cn-shanghai.aliyuncs.com |
| 华北1（青岛） | cn-qingdao | https://oss-cn-qingdao.aliyuncs.com |
| 华北2（北京） | cn-beijing | https://oss-cn-beijing.aliyuncs.com |
| 华北3（张家口） | cn-zhangjiakou | https://oss-cn-zhangjiakou.aliyuncs.com |
| 华北5（呼和浩特） | cn-huhehaote | https://oss-cn-huhehaote.aliyuncs.com |
| 华南1（深圳） | cn-shenzhen | https://oss-cn-shenzhen.aliyuncs.com |
| 华南2（河源） | cn-heyuan | https://oss-cn-heyuan.aliyuncs.com |
| 华南3（广州） | cn-guangzhou | https://oss-cn-guangzhou.aliyuncs.com |
| 西南1（成都） | cn-chengdu | https://oss-cn-chengdu.aliyuncs.com |
| 中国（香港） | cn-hongkong | https://oss-cn-hongkong.aliyuncs.com |

**如何查看你的 Bucket 地域**：
- 在 OSS 控制台 → Bucket 列表
- 找到你的 Bucket，查看"地域"列

### 步骤 5：填写 .env 文件

在服务器上编辑 `.env` 文件：

```bash
cd /var/www/geshixiugai
vi .env
```

填入以下内容（**删除所有注释和示例**）：

```bash
OSS_ACCESS_KEY_ID=你的AccessKey ID
OSS_ACCESS_KEY_SECRET=你的AccessKey Secret
OSS_BUCKET_NAME=word-formatter-storage
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_REGION=cn-hangzhou
```

**示例**（替换为你的实际值）：
```bash
OSS_ACCESS_KEY_ID=LTAI5txxxxxxxxxxxxxxxxxxxx
OSS_ACCESS_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OSS_BUCKET_NAME=word-formatter-storage
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_REGION=cn-hangzhou
```

**保存文件**：
- 使用 vi：按 `Esc`，输入 `:wq`，按 `Enter`

---

## 💰 费用说明

### 免费额度

阿里云 OSS 提供：
- **存储容量**：无免费额度（按实际使用量计费）
- **外网下行流量**：无免费额度（按实际使用量计费）
- **内网流量**：免费（同地域访问）

### 计费方式

- **存储费用**：约 0.12 元/GB/月
- **外网流量**：约 0.5 元/GB
- **请求费用**：PUT/COPY/POST/LIST 请求约 0.01 元/万次

### 成本估算

对于个人项目（假设）：
- 存储 10GB：约 1.2 元/月
- 外网流量 10GB/月：约 5 元/月
- **总计**：约 6-10 元/月

**提示**：如果服务器和 OSS 在同一地域，使用内网访问，流量费用为 0。

---

## 🔒 安全建议

### 1. 使用子账号 AccessKey

1. 访问：https://ram.console.aliyun.com/
2. 创建子账号
3. 授予 OSS 相关权限
4. 使用子账号的 AccessKey

### 2. 设置 Bucket 权限

- **读写权限**：设置为"私有"（推荐）
- **跨域设置**：如果需要，配置 CORS 规则

### 3. 定期更换 AccessKey

- 建议每 3-6 个月更换一次 AccessKey
- 更换后更新 `.env` 文件并重启服务

---

## ✅ 验证配置

配置完成后，重启服务并测试：

```bash
# 重启服务
sudo systemctl restart geshixiugai

# 查看日志，确认使用了 OSS
sudo journalctl -u geshixiugai -f
# 应该看到：[Storage] Using Alibaba Cloud OSS
```

---

## 📞 需要帮助？

如果遇到问题：
1. 检查 AccessKey 是否正确
2. 检查 Bucket 名称是否正确
3. 检查 Endpoint 和 Region 是否匹配
4. 查看服务日志：`sudo journalctl -u geshixiugai -n 50`

---

## 🎉 优势总结

使用阿里云 OSS 的优势：
- ✅ 与服务器同地域，访问速度快
- ✅ 内网流量免费
- ✅ 稳定可靠，官方服务
- ✅ 管理方便，统一控制台

**推荐：如果你的服务器在阿里云，使用阿里云 OSS 是最佳选择！** 🚀





