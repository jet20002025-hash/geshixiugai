# 服务启动失败 - status=3 修复步骤

## 🔍 问题分析

`status=3/NOTIMPLEMENTED` 表示：
- Gunicorn 可以启动
- 但应用（FastAPI）启动时出错
- 通常是代码导入错误或缺少依赖

---

## 🚀 修复步骤

### 步骤 1：查看详细错误日志

在服务器终端执行：

```bash
# 查看最近的详细日志
sudo journalctl -u geshixiugai -n 100 --no-pager
```

**把错误信息发给我，我帮你分析！**

---

### 步骤 2：手动测试启动（查看具体错误）

```bash
# 进入项目目录
cd /var/www/geshixiugai

# 激活虚拟环境
source venv/bin/activate

# 手动启动，查看具体错误
gunicorn -c gunicorn_config.py backend.app.main:app
```

**这会显示详细的错误信息，把错误信息发给我！**

---

### 步骤 3：检查代码导入

```bash
# 确保在项目目录和虚拟环境中
cd /var/www/geshixiugai
source venv/bin/activate

# 测试导入
python -c "from backend.app.main import app; print('✅ 导入成功')"
```

如果报错，把错误信息发给我。

---

## 🔧 常见问题和解决方案

### 问题 1：缺少 weasyprint（最可能）

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 安装 weasyprint
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint

# 验证
python -c "import weasyprint; print('✅ WeasyPrint 安装成功')"

# 退出虚拟环境
deactivate

# 重启服务
sudo systemctl restart geshixiugai
```

### 问题 2：缺少其他依赖

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate

# 重启服务
sudo systemctl restart geshixiugai
```

### 问题 3：代码错误（导入问题）

```bash
cd /var/www/geshixiugai
source venv/bin/activate

# 测试导入
python -c "from backend.app.main import app"

# 如果报错，查看具体错误
```

---

## 📋 完整修复流程

在服务器终端依次执行：

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 更新代码（确保有最新代码）
git pull origin main

# 4. 安装所有依赖
pip install -r requirements.txt

# 5. 特别确保 weasyprint 已安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint

# 6. 验证导入
python -c "from backend.app.main import app; print('✅ 导入成功')"

# 7. 如果导入成功，手动测试启动
gunicorn -c gunicorn_config.py backend.app.main:app
# 按 Ctrl+C 停止测试

# 8. 退出虚拟环境
deactivate

# 9. 重启服务
sudo systemctl restart geshixiugai

# 10. 检查状态
sudo systemctl status geshixiugai
```

---

## ⚠️ 重要提示

**先执行步骤 1 和 2，把错误信息发给我，我可以帮你精确定位问题！**

特别是：
- `sudo journalctl -u geshixiugai -n 100 --no-pager` 的输出
- `gunicorn -c gunicorn_config.py backend.app.main:app` 的错误信息

---

**现在执行步骤 1 和 2，把错误信息发给我！** 🔍

