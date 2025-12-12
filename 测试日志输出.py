#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试日志输出功能"""

import sys

def _log_to_file(message: str) -> None:
    """将日志消息同时输出到 stderr 和日志文件（双重保险）"""
    print(message, file=sys.stderr, flush=True)
    try:
        with open("/var/log/geshixiugai/error.log", "a") as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"写入日志文件失败: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("测试日志输出功能...")
    _log_to_file("[测试] 这是一条测试日志消息")
    print("测试完成！请检查 /var/log/geshixiugai/error.log")

