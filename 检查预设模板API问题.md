# 检查预设模板API问题

## ✅ 文件存在

文件已存在：`/var/www/geshixiugai/backend/app/services/university_templates.json`

---

## 🔍 下一步检查

### 步骤 1：检查文件内容是否正确

```bash
# 查看文件前几行
head -10 /var/www/geshixiugai/backend/app/services/university_templates.json

# 检查JSON格式
python3 -m json.tool /var/www/geshixiugai/backend/app/services/university_templates.json > /dev/null
echo $?
# 如果返回0，说明JSON格式正确
```

### 步骤 2：测试API端点

```bash
# 在服务器上测试API
curl http://localhost:8000/templates/presets

# 或者测试外部访问
curl https://geshixiugai.cn/templates/presets
```

**应该返回**：
```json
[
  {
    "id": "hdu",
    "name": "杭州电子科技大学",
    "display_name": "杭州电子科技大学",
    "description": "..."
  },
  ...
]
```

### 步骤 3：查看服务器日志

```bash
# 查看最近的日志
sudo journalctl -u geshixiugai -n 100 --no-pager | grep -i "template\|university\|preset"

# 或者查看所有最近的错误
sudo journalctl -u geshixiugai -n 100 --no-pager | tail -50
```

### 步骤 4：检查服务是否正常运行

```bash
# 检查服务状态
sudo systemctl status geshixiugai

# 检查服务是否在监听8000端口
sudo netstat -tlnp | grep 8000
# 或
sudo ss -tlnp | grep 8000
```

### 步骤 5：检查代码是否已更新

```bash
# 检查API路由是否存在
grep -r "presets" /var/www/geshixiugai/backend/app/api/templates.py

# 检查服务类是否存在
grep -r "UniversityTemplateService" /var/www/geshixiugai/backend/app/api/templates.py
```

---

## 🔧 可能的问题

### 问题1：API路由未注册

**检查**：
```bash
grep -A 5 "/presets" /var/www/geshixiugai/backend/app/api/templates.py
```

**如果不存在**，需要更新代码。

### 问题2：服务未重启

**解决**：
```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

### 问题3：文件权限问题

**检查**：
```bash
ls -la /var/www/geshixiugai/backend/app/services/university_templates.json
```

**如果权限不对**：
```bash
chmod 644 /var/www/geshixiugai/backend/app/services/university_templates.json
chown nginx:nginx /var/www/geshixiugai/backend/app/services/university_templates.json
```

### 问题4：Python导入错误

**检查日志**：
```bash
sudo journalctl -u geshixiugai -n 200 --no-pager | grep -i "error\|exception\|traceback"
```

---

## 📋 完整检查命令（复制粘贴）

```bash
# 1. 检查文件内容
head -10 /var/www/geshixiugai/backend/app/services/university_templates.json

# 2. 检查JSON格式
python3 -m json.tool /var/www/geshixiugai/backend/app/services/university_templates.json > /dev/null && echo "JSON格式正确" || echo "JSON格式错误"

# 3. 测试API
curl http://localhost:8000/templates/presets

# 4. 查看日志
sudo journalctl -u geshixiugai -n 100 --no-pager | grep -i "template\|university"

# 5. 检查服务状态
sudo systemctl status geshixiugai

# 6. 检查API路由
grep -A 3 "/presets" /var/www/geshixiugai/backend/app/api/templates.py
```

---

## 🚀 如果API测试失败

### 方法1：重启服务

```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

### 方法2：更新代码

```bash
cd /var/www/geshixiugai
git pull origin main
sudo systemctl restart geshixiugai
```

### 方法3：检查Nginx配置

```bash
# 检查Nginx是否正常转发
sudo nginx -t
sudo systemctl status nginx
```

---

**请执行上面的检查命令，并告诉我结果！** 🔍







