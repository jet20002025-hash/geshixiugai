# 安装 WeasyPrint - 快速命令

## ✅ 系统依赖已安装

现在只需要安装 Python 包。

## 🚀 快速安装命令

```bash
cd /var/www/geshixiugai

# 确保在虚拟环境中
source venv/bin/activate

# 安装兼容版本组合（避免 transform 错误）
pip install weasyprint==60.2 pypdf==3.15.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## ✅ 验证安装

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 检查 WeasyPrint
python -c "import weasyprint; print('WeasyPrint版本:', weasyprint.__version__)"

# 检查 pypdf
python -c "import pypdf; print('pypdf版本:', pypdf.__version__)"

# 测试导入
python -c "from weasyprint import HTML; print('✅ WeasyPrint导入成功')"
```

## 🔄 重启服务

```bash
sudo systemctl restart geshixiugai
sudo systemctl status geshixiugai
```

## 📝 更新 requirements.txt（可选）

如果使用新版本，可以更新 requirements.txt：

```bash
# 查看当前安装的版本
pip freeze | grep -E "weasyprint|pypdf"
```

然后手动更新 requirements.txt 文件。

