# gunicorn_config.py
import multiprocessing
import os
from pathlib import Path

# 工作目录（项目根目录）
chdir = str(Path(__file__).parent)

# 绑定地址和端口
bind = "127.0.0.1:8000"

# Worker 数量（根据 CPU 核心数调整，建议：CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型（使用 Uvicorn worker 以支持异步）
worker_class = "uvicorn.workers.UvicornWorker"

# 超时设置（秒）
timeout = 120
keepalive = 5

# 请求限制（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = "/var/log/geshixiugai/access.log"
errorlog = "/var/log/geshixiugai/error.log"
loglevel = "info"

# 进程名称
proc_name = "geshixiugai"

# 工作模式
daemon = False

# 用户和组（在生产环境中由 systemd 管理）
# user = "www-data"
# group = "www-data"


