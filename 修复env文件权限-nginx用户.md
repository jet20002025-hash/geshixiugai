# 修复 .env 文件权限（nginx 用户）

## 当前状态

```
-rw------- 1 nginx nginx 2783 Dec  1 20:22 .env
```

文件所有者是 `nginx`，权限是 `600`（只有所有者可以读写）。

## 解决方案

### 方法1：修改文件所有者和权限（推荐）

```bash
cd /var/www/geshixiugai

# 修改所有者为 admin（或运行服务的用户）
sudo chown admin:admin .env

# 修改权限为 644（所有者读写，组和其他用户只读）
chmod 644 .env

# 验证
ls -la .env
# 应该显示：-rw-r--r-- 1 admin admin ... .env
```

### 方法2：如果服务以 nginx 用户运行

如果 Gunicorn 服务以 `nginx` 用户运行，可以保持所有者为 `nginx`，但需要调整权限：

```bash
cd /var/www/geshixiugai

# 修改权限为 644（允许组和其他用户读取）
sudo chmod 644 .env

# 验证
ls -la .env
# 应该显示：-rw-r--r-- 1 nginx nginx ... .env
```

### 方法3：检查服务运行用户

```bash
# 查看 systemd 服务配置，确认运行用户
cat /etc/systemd/system/geshixiugai.service | grep User

# 或者查看服务状态
sudo systemctl status geshixiugai | grep "Main PID"
ps aux | grep gunicorn
```

## 推荐操作

```bash
cd /var/www/geshixiugai

# 1. 修改所有者为 admin（通常服务以 admin 用户运行）
sudo chown admin:admin .env

# 2. 修改权限
chmod 644 .env

# 3. 验证
ls -la .env

# 4. 测试应用导入
source venv/bin/activate
python -c "from backend.app.main import app; print('✅ 应用导入成功')"

# 5. 如果成功，启动服务
sudo systemctl start geshixiugai
sudo systemctl status geshixiugai
```

