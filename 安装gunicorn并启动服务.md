# 安装 gunicorn 并启动服务

## 🔍 问题确认

gunicorn 未安装，需要安装。

---

## 🚀 安装步骤

### 步骤 1：进入项目目录并激活虚拟环境

```bash
cd /var/www/geshixiugai
source venv/bin/activate
```

### 步骤 2：安装 gunicorn

```bash
pip install gunicorn
```

### 步骤 3：验证安装

```bash
# 检查 gunicorn 是否安装成功
which gunicorn
gunicorn --version
```

应该显示 gunicorn 的路径和版本号。

### 步骤 4：手动测试启动（可选）

```bash
# 测试启动（按 Ctrl+C 停止）
gunicorn -c gunicorn_config.py backend.app.main:app
```

如果看到类似 `[INFO] Starting gunicorn` 的输出，说明可以启动。

### 步骤 5：重启服务

```bash
# 退出虚拟环境（如果还在）
deactivate

# 重启服务
sudo systemctl restart geshixiugai

# 检查服务状态
sudo systemctl status geshixiugai
```

---

## 📋 完整命令（复制粘贴）

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装 gunicorn
pip install gunicorn

# 4. 验证安装
gunicorn --version

# 5. 退出虚拟环境
deactivate

# 6. 重启服务
sudo systemctl restart geshixiugai

# 7. 检查状态
sudo systemctl status geshixiugai
```

---

## ✅ 预期结果

安装完成后，服务应该能正常启动：

```bash
sudo systemctl status geshixiugai
```

应该显示：
```
Active: active (running)
```

---

## 🔍 如果还有问题

如果安装后还是失败，查看详细错误：

```bash
# 查看服务日志
sudo journalctl -u geshixiugai -n 100

# 检查 gunicorn 路径
ls -la /var/www/geshixiugai/venv/bin/gunicorn
```

---

**现在执行安装命令！** 🚀





