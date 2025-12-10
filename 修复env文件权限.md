# 修复 .env 文件权限问题

## 问题

`PermissionError: [Errno 13] Permission denied: '/var/www/geshixiugai/.env'`

服务无法读取 `.env` 文件，因为权限不足。

## 解决方案

### 方法1：修复文件权限（推荐）

```bash
cd /var/www/geshixiugai

# 检查当前权限
ls -la .env

# 修复权限（允许所有者读写，组和其他用户只读）
chmod 644 .env

# 确保文件所有者正确
sudo chown admin:admin .env

# 再次检查权限
ls -la .env
```

### 方法2：如果文件不存在，创建它

```bash
cd /var/www/geshixiugai

# 检查文件是否存在
ls -la .env

# 如果不存在，从示例文件创建
if [ ! -f .env ]; then
    cp env.example .env
    chmod 644 .env
    chown admin:admin .env
    echo "✅ .env 文件已创建，请编辑它并填入正确的配置"
fi
```

### 方法3：检查整个目录的权限

```bash
cd /var/www/geshixiugai

# 检查目录权限
ls -la | grep -E "^d.*geshixiugai|\.env"

# 如果需要，修复整个项目目录的权限
sudo chown -R admin:admin /var/www/geshixiugai
find /var/www/geshixiugai -type f -name "*.env" -exec chmod 644 {} \;
```

## 完整修复流程

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 检查 .env 文件
ls -la .env

# 3. 修复权限
chmod 644 .env
sudo chown admin:admin .env

# 4. 验证权限
ls -la .env
# 应该显示：-rw-r--r-- 1 admin admin ... .env

# 5. 测试应用导入
source venv/bin/activate
python -c "from backend.app.main import app; print('✅ 应用导入成功')"

# 6. 如果成功，启动服务
sudo systemctl start geshixiugai

# 7. 检查服务状态
sudo systemctl status geshixiugai
```

## 常见权限问题

### 问题1：文件权限太严格

**症状**: `Permission denied`

**解决**: 
```bash
chmod 644 .env
```

### 问题2：文件所有者不正确

**症状**: 即使权限看起来正确，仍然无法读取

**解决**:
```bash
sudo chown admin:admin .env
```

### 问题3：目录权限问题

**症状**: 无法访问包含 `.env` 的目录

**解决**:
```bash
chmod 755 /var/www/geshixiugai
```


