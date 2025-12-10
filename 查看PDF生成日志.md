# 查看 PDF 生成日志

## 查看完整的文档处理日志

```bash
# 查看包含 PDF 生成相关的所有日志
sudo journalctl -u geshixiugai --since "10 minutes ago" --no-pager | grep -E "\[预览\]|\[PDF预览\]|\[存储\]" | tail -100
```

## 关键日志标识

查找以下关键日志：

### PDF 生成开始
- `[预览] 开始生成PDF预览: ...`
- `[PDF预览] 开始生成PDF预览，输入文件: ...`
- `[PDF预览] WeasyPrint导入成功`

### PDF 生成过程
- `[PDF预览] 开始生成HTML预览: ...`
- `[PDF预览] 开始转换HTML到PDF，HTML大小: ... KB`
- `[PDF预览] HTML中包含 X 个img标签，其中 Y 个使用data URI`
- `[PDF预览] 开始生成PDF文件...`

### PDF 生成结果
- `[PDF预览] PDF生成成功，大小: ... KB` ✅
- `[PDF预览] 生成PDF失败: ...` ❌
- `[预览] ✅ PDF预览生成成功: ...` ✅
- `[预览] PDF生成失败，回退到HTML预览` ❌

### 存储相关
- `[存储] 准备上传文件: pdf -> ...`
- `[存储] ✅ 成功上传: documents/.../pdf.pdf` ✅
- `[存储] PDF文件不存在，检查HTML文件` ❌

## 如果看不到 PDF 生成日志

如果日志中没有 `[PDF预览]` 相关的信息，说明 PDF 生成根本没有执行。可能的原因：

1. **代码没有更新**：服务器上的代码可能还是旧版本
   ```bash
   cd /var/www/geshixiugai
   git log --oneline -1
   # 应该看到最新的提交：247eb83 fix: 删除文件开头错误添加的错误信息文本
   ```

2. **文档是在修复之前处理的**：需要重新上传文档

## 查看特定文档的处理日志

```bash
# 替换为实际的文档ID
DOCUMENT_ID="45ad9acdf55e4314a13bdb20a3ff2bb3"

# 查看该文档的处理日志
sudo journalctl -u geshixiugai --since "30 minutes ago" --no-pager | grep -E "$DOCUMENT_ID|\[预览\]|\[PDF预览\]" | tail -50
```


