# 查看PDF生成日志指南

## 方法1：查看最近的日志（推荐）

```bash
# 查看最近200行日志，包含预览相关的内容
sudo journalctl -u geshixiugai -n 200 --no-pager | grep -E "预览|PDF|存储"

# 或者查看所有最近的日志（不筛选）
sudo journalctl -u geshixiugai -n 200 --no-pager
```

## 方法2：实时监控（需要先上传文档）

```bash
# 先上传一个文档，然后立即执行这个命令
sudo journalctl -u geshixiugai -f
```

## 方法3：查看特定时间段的日志

```bash
# 查看最近5分钟的日志
sudo journalctl -u geshixiugai --since "5 minutes ago" --no-pager | grep -E "预览|PDF|存储"

# 查看今天的日志
sudo journalctl -u geshixiugai --since today --no-pager | grep -E "预览|PDF|存储"
```

## 方法4：查看完整的处理流程

```bash
# 查看包含"预览"、"PDF"、"存储"的所有日志
sudo journalctl -u geshixiugai --since "10 minutes ago" --no-pager | grep -iE "预览|pdf|存储|preview|storage"
```

## 关键日志标识

查找以下关键日志：
- `[预览] 开始生成PDF预览`
- `[PDF预览] 开始生成PDF预览`
- `[PDF预览] WeasyPrint导入成功`
- `[PDF预览] weasyprint未安装`
- `[PDF预览] PDF生成成功`
- `[PDF预览] 生成PDF失败`
- `[存储] 准备上传文件: pdf`
- `[存储] ✅ 成功上传`

## 如果还是没有日志

1. 确认服务正在运行：
```bash
sudo systemctl status geshixiugai
```

2. 确认代码已更新：
```bash
cd /var/www/geshixiugai
git log --oneline -5
```

3. 重新上传一个文档，然后立即查看日志：
```bash
# 在一个终端上传文档
# 在另一个终端执行：
sudo journalctl -u geshixiugai -f --since "1 minute ago"
```

