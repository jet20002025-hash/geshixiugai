"""
Vercel Serverless Function 入口
适配 FastAPI 应用
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.main import create_app

# 创建 FastAPI 应用实例
app = create_app()

# Vercel 需要导出 app 对象
__all__ = ["app"]

