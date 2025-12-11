# 排查SSH连接问题

## 问题：Permission denied

可能的原因和解决方案：

### 1. 密码错误
- 确认服务器密码是否正确
- 注意大小写和特殊字符

### 2. 服务器禁用了密码登录
如果服务器只允许SSH密钥登录，需要：
- 使用SSH密钥登录
- 或者临时启用密码登录

### 3. 使用SSH密钥（推荐）

如果已有SSH密钥：
```bash
# 使用SSH密钥上传
scp -i ~/.ssh/id_rsa SIMSUN.TTC admin@121.199.49.1:/tmp/simsun.ttc
```

如果没有SSH密钥，可以生成：
```bash
# 生成SSH密钥对
ssh-keygen -t rsa -b 4096

# 将公钥复制到服务器
ssh-copy-id admin@121.199.49.1
```

### 4. 替代方案：使用SFTP客户端

如果scp无法连接，可以使用图形化工具：
- **FileZilla** (免费，支持SFTP)
- **Cyberduck** (Mac免费)
- **Transmit** (Mac付费)

连接信息：
- 协议：SFTP
- 主机：121.199.49.1
- 用户名：admin
- 端口：22

### 5. 在服务器上直接下载

如果无法从本地上传，可以在服务器上直接下载字体：

```bash
# 在服务器上执行
cd /tmp

# 从Windows字体CDN下载（如果有公开链接）
# 或者使用其他方式获取字体文件
```

### 6. 检查服务器SSH配置

在服务器上检查SSH配置：
```bash
sudo cat /etc/ssh/sshd_config | grep -E "PasswordAuthentication|PubkeyAuthentication"
```

如果需要启用密码登录：
```bash
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

