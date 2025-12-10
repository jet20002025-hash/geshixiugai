# 卸载 LibreOffice

## 🗑️ 卸载命令

### CentOS/RHEL/Alibaba Cloud Linux

```bash
# 卸载 LibreOffice
sudo yum remove -y libreoffice-headless libreoffice

# 清理相关依赖（可选）
sudo yum autoremove -y
```

### Ubuntu/Debian

```bash
# 卸载 LibreOffice
sudo apt remove -y libreoffice libreoffice-core

# 清理相关依赖（可选）
sudo apt autoremove -y
```

## ✅ 验证卸载

```bash
# 检查是否已卸载
which libreoffice
libreoffice --version

# 应该显示 "command not found" 或类似错误
```

## 📝 注意事项

- 卸载后，代码会自动回退到 WeasyPrint
- 不会影响现有的 PDF 生成功能
- 可以随时重新安装（如果需要）


