# 解决 process_document 错误

## 🔍 错误原因

错误信息：`DocumentService.process_document() got an unexpected keyword argument 'university_id'`

**原因**：服务器上的代码还没有更新，使用的是旧版本的代码，旧版本没有 `university_id` 参数。

---

## 🔧 解决方案

### 步骤 1：确保本地代码已提交

在你的电脑上检查：

```bash
cd /Users/zwj/word格式修改器

# 检查是否有未提交的修改
git status

# 如果有修改，提交并推送
git add .
git commit -m "修复：添加 university_id 参数支持"
git push origin main
```

### 步骤 2：在服务器上拉取最新代码

```bash
# 在服务器上执行（使用阿里云控制台网页终端或SSH）
cd /var/www/geshixiugai

# 拉取最新代码
git pull origin main

# 检查是否拉取成功
git log -1
# 应该看到最新的提交
```

### 步骤 3：重启服务

```bash
# 重启服务
sudo systemctl restart geshixiugai

# 检查服务状态
sudo systemctl status geshixiugai

# 查看服务日志（如果有错误）
sudo journalctl -u geshixiugai -n 50 --no-pager
```

---

## 🔍 验证代码版本

### 检查服务器上的代码

```bash
# 在服务器上执行
cd /var/www/geshixiugai

# 检查 process_document 方法定义
grep -A 5 "async def process_document" backend/app/services/document_service.py
```

**应该看到**：
```python
async def process_document(
    self, 
    template_id: Optional[str] = None, 
    university_id: Optional[str] = None,
    upload: Optional[UploadFile] = None
) -> Tuple[str, Dict]:
```

**如果看到**（旧版本）：
```python
async def process_document(
    self, 
    template_id: str, 
    upload: UploadFile
) -> Tuple[str, Dict]:
```

说明代码还没有更新，需要拉取最新代码。

---

## 📋 完整操作流程

### 在你的电脑上

```bash
cd /Users/zwj/word格式修改器

# 检查并提交代码
git status
git add .
git commit -m "修复：添加 university_id 参数支持"
git push origin main
```

### 在服务器上

```bash
# 连接服务器
ssh root@121.199.49.1
# 或使用阿里云控制台网页终端

# 进入项目目录
cd /var/www/geshixiugai

# 拉取最新代码
git pull origin main

# 验证代码已更新
grep -A 5 "async def process_document" backend/app/services/document_service.py

# 重启服务
sudo systemctl restart geshixiugai

# 检查服务状态
sudo systemctl status geshixiugai
```

---

## ⚠️ 如果还是出错

### 检查 Python 缓存

```bash
# 在服务器上执行
cd /var/www/geshixiugai

# 清除 Python 缓存
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 重启服务
sudo systemctl restart geshixiugai
```

### 检查虚拟环境

```bash
# 确保使用正确的虚拟环境
cd /var/www/geshixiugai
source venv/bin/activate

# 检查 Python 路径
which python
# 应该显示：/var/www/geshixiugai/venv/bin/python
```

---

## ✅ 验证修复

### 测试上传文档

1. 访问网站
2. 上传文档（使用预设模板或自定义模板）
3. 应该不再出现错误

### 检查日志

```bash
# 查看服务日志
sudo journalctl -u geshixiugai -f
# 按 Ctrl+C 退出
```

---

## 📝 总结

**问题**：服务器代码版本过旧，没有 `university_id` 参数

**解决**：
1. 确保本地代码已提交到 GitHub
2. 在服务器上拉取最新代码
3. 重启服务

**现在执行**：在服务器上执行 `git pull origin main` 然后重启服务！🚀

