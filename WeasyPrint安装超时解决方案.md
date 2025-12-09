# WeasyPrint 安装超时解决方案

## 🔍 问题原因

安装 WeasyPrint 时出现 `Connection timed out` 是因为：
1. **网络问题**：国内访问 PyPI 官方源较慢
2. **文件较大**：fonttools 包有 5.0 MB，下载需要时间
3. **连接超时**：默认超时时间可能不够

---

## ✅ 解决方案：使用国内镜像源

### 方法 1：使用清华镜像源（推荐）

在阿里云服务器的远程连接终端里执行：

```bash
# 进入项目目录
cd /var/www/geshixiugai

# 激活虚拟环境（如果有）
source venv/bin/activate  # 或 source .venv/bin/activate

# 使用清华镜像源安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint
```

### 方法 2：使用阿里云镜像源

```bash
pip install -i https://mirrors.aliyun.com/pypi/simple/ weasyprint
```

### 方法 3：使用豆瓣镜像源

```bash
pip install -i https://pypi.douban.com/simple/ weasyprint
```

### 方法 4：永久配置镜像源（推荐）

如果经常需要安装包，可以永久配置镜像源：

```bash
# 创建 pip 配置目录
mkdir -p ~/.pip

# 创建配置文件
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 然后正常安装即可
pip install weasyprint
```

---

## 🔧 如果还是超时，增加超时时间

```bash
# 增加超时时间到 300 秒
pip install --timeout 300 -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint
```

---

## 📋 完整安装命令（推荐）

在阿里云服务器的远程连接终端里，执行：

```bash
# 1. 进入项目目录
cd /var/www/geshixiugai

# 2. 激活虚拟环境（如果有）
source venv/bin/activate

# 3. 使用清华镜像源安装（增加超时时间）
pip install --timeout 300 -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint

# 4. 验证安装
python -c "import weasyprint; print('安装成功！版本:', weasyprint.__version__)"
```

---

## 🚀 如果下载中断，可以重试

pip 会自动断点续传，如果下载中断：

1. **直接重新执行安装命令**（pip 会继续下载）
2. **或者清除缓存后重试**：

```bash
# 清除 pip 缓存
pip cache purge

# 重新安装
pip install --timeout 300 -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint
```

---

## ⚡ 快速解决方案

**最简单的方法，直接复制执行：**

```bash
cd /var/www/geshixiugai && \
source venv/bin/activate 2>/dev/null || true && \
pip install --timeout 300 -i https://pypi.tuna.tsinghua.edu.cn/simple weasyprint && \
python -c "import weasyprint; print('✅ WeasyPrint 安装成功！版本:', weasyprint.__version__)"
```

---

## 📝 其他镜像源地址

如果清华源也慢，可以尝试：

```bash
# 阿里云镜像
pip install -i https://mirrors.aliyun.com/pypi/simple/ weasyprint

# 中科大镜像
pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ weasyprint

# 豆瓣镜像
pip install -i https://pypi.douban.com/simple/ weasyprint

# 华为云镜像
pip install -i https://mirrors.huaweicloud.com/repository/pypi/simple/ weasyprint
```

---

## ✅ 验证安装成功

安装完成后，执行：

```bash
python -c "import weasyprint; print('✅ 安装成功！版本:', weasyprint.__version__)"
```

如果看到版本号，说明安装成功！

---

## 🔄 安装完成后

```bash
# 重启服务
sudo systemctl restart geshixiugai

# 检查服务状态
sudo systemctl status geshixiugai
```

---

## 💡 小贴士

1. **使用镜像源**：国内访问 PyPI 官方源很慢，建议使用国内镜像
2. **增加超时时间**：大文件下载需要更长时间
3. **断点续传**：pip 支持断点续传，中断后可以继续
4. **永久配置**：如果经常安装包，建议永久配置镜像源

---

**记住：在阿里云控制台的远程连接终端里执行这些命令！** 🎯

