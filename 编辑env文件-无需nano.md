# 编辑 .env 文件 - 无需 nano

## 🎯 问题

服务器上没有 `nano` 编辑器。

## ✅ 解决方案

### 方法 1：使用 vi/vim 编辑器（系统自带）

```bash
cd /var/www/geshixiugai
vi .env
```

**vi/vim 使用方法**：
1. **进入编辑模式**：按 `i` 键
2. **编辑内容**：使用方向键移动，删除并输入内容
3. **保存退出**：
   - 按 `Esc` 键退出编辑模式
   - 输入 `:wq` 然后按 `Enter`（保存并退出）
   - 或者 `:q!` 然后按 `Enter`（不保存退出）

### 方法 2：使用 echo 命令直接创建（最简单 ⭐）

如果你知道配置内容，可以直接用命令创建：

```bash
cd /var/www/geshixiugai

# 创建 .env 文件（使用 Supabase 示例）
cat > .env << 'EOF'
SUPABASE_URL=https://你的项目ID.supabase.co
SUPABASE_KEY=你的service_role key
SUPABASE_BUCKET=word-formatter-storage
EOF
```

**或者使用 R2**：
```bash
cat > .env << 'EOF'
R2_ACCOUNT_ID=你的Account ID
R2_ACCESS_KEY_ID=你的Access Key ID
R2_SECRET_ACCESS_KEY=你的Secret Access Key
R2_BUCKET_NAME=word-formatter-storage
R2_ENDPOINT=https://你的Account ID.r2.cloudflarestorage.com
EOF
```

### 方法 3：安装 nano（可选）

```bash
# CentOS/RHEL/Alinux
sudo dnf install -y nano
# 或者
sudo yum install -y nano

# 然后使用
nano .env
```

---

## 🚀 推荐操作流程

### 步骤 1：先拉取最新代码

```bash
cd /var/www/geshixiugai
git pull origin main
```

### 步骤 2：编辑 .env 文件

**使用 vi**：
```bash
vi .env
# 按 i 进入编辑模式
# 编辑内容
# 按 Esc，然后输入 :wq 保存退出
```

**或使用 cat 命令**（如果知道配置内容）：
```bash
cat > .env << 'EOF'
SUPABASE_URL=你的URL
SUPABASE_KEY=你的KEY
SUPABASE_BUCKET=word-formatter-storage
EOF
```

### 步骤 3：继续部署

```bash
sudo ./deploy_aliyun.sh
```

---

## 💡 vi/vim 常用命令

- `i` - 进入插入模式（开始编辑）
- `Esc` - 退出插入模式
- `:w` - 保存
- `:q` - 退出
- `:wq` - 保存并退出
- `:q!` - 不保存强制退出
- `dd` - 删除当前行
- `/搜索内容` - 搜索

---

**推荐：先拉取代码，然后用 vi 编辑 .env 文件！** 🚀





