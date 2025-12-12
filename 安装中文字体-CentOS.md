# 在 CentOS/RHEL/Alibaba Cloud Linux 上安装中文字体

## 方法1：使用 EPEL 仓库安装（推荐）

```bash
# 1. 安装 EPEL 仓库（如果还没有）
sudo yum install -y epel-release

# 2. 搜索可用的中文字体包
sudo yum search font | grep -i chinese

# 3. 安装中文字体（根据搜索结果选择）
# 常见包名：
sudo yum install -y wqy-microhei-fonts
# 或者
sudo yum install -y wqy-zenhei-fonts
# 或者
sudo yum install -y cjkuni-uming-fonts cjkuni-ukai-fonts
```

## 方法2：手动下载并安装字体文件

如果 yum 仓库中没有字体包，可以手动下载安装：

```bash
# 1. 创建字体目录
sudo mkdir -p /usr/share/fonts/chinese

# 2. 下载字体文件（以文泉驿字体为例）
cd /tmp
wget https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc
# 或者使用其他中文字体源

# 3. 复制字体文件到系统字体目录
sudo cp wqy-microhei.ttc /usr/share/fonts/chinese/

# 4. 更新字体缓存
sudo fc-cache -fv

# 5. 验证字体安装
fc-list :lang=zh | grep -i wqy
```

## 方法3：从系统字体目录复制（如果有其他软件已安装）

```bash
# 检查系统中是否已有中文字体
find /usr/share/fonts -name "*song*" -o -name "*hei*" -o -name "*sim*" 2>/dev/null

# 如果找到字体文件，确保字体缓存已更新
sudo fc-cache -fv
```

## 方法4：使用阿里云镜像源（如果在中国）

```bash
# 备份原配置
sudo cp /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup

# 使用阿里云镜像（根据你的系统版本选择）
# CentOS 7:
sudo sed -e 's|^mirrorlist=|#mirrorlist=|g' \
         -e 's|^#baseurl=http://mirror.centos.org|baseurl=https://mirrors.aliyun.com|g' \
         -i /etc/yum.repos.d/CentOS-*.repo

# 然后重试安装
sudo yum clean all
sudo yum makecache
sudo yum install -y wqy-microhei-fonts
```

## 验证字体安装

```bash
# 检查字体是否安装成功
fc-list :lang=zh

# 检查 WeasyPrint 能否找到字体
python3 -c "from weasyprint import HTML; print('WeasyPrint 可用')"
```

## 安装后重启服务

```bash
sudo systemctl restart geshixiugai
```




