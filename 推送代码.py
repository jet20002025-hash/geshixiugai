#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动提交并推送到 GitHub"""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, description):
    """执行命令并显示输出"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print('='*50)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
            return False
        else:
            print(f"✅ 命令执行成功")
            return True
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False

def main():
    commit_msg = "修复检测日志输出：使用sys.stderr确保Gunicorn捕获输出"
    
    print("开始提交并推送到 GitHub...")
    
    # 1. 检查状态
    if not run_cmd("git status --short", "检查 Git 状态"):
        return
    
    # 2. 添加文件
    if not run_cmd("git add -A", "添加所有更改"):
        return
    
    # 3. 提交
    if not run_cmd(f'git commit -m "{commit_msg}"', "提交更改"):
        return
    
    # 4. 推送
    if not run_cmd("git push origin main", "推送到 GitHub"):
        return
    
    # 5. 显示最新提交
    run_cmd("git log --oneline -1", "显示最新提交")
    
    print("\n" + "="*50)
    print("✅ 完成！代码已推送到 GitHub")
    print("="*50)

if __name__ == "__main__":
    main()

