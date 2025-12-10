import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from .routers import template_router, document_router, payment_router

# 加载 .env 文件（如果存在）
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # 也尝试从当前目录加载
    load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(
        title="论文格式自动修复平台",
        description="根据上传的模板自动修复毕业论文 Word 文档格式的服务",
        version="0.1.0",
    )

    # 全局异常处理，确保所有错误都返回 JSON
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc) if os.getenv("VERCEL_ENV") != "production" else "服务器内部错误，请稍后重试"
            }
        )

    app.include_router(template_router, prefix="/templates", tags=["templates"])
    app.include_router(document_router, prefix="/documents", tags=["documents"])
    app.include_router(payment_router, prefix="/payments", tags=["payments"])

    # 处理 favicon 请求，避免 404 错误
    @app.get("/favicon.ico", include_in_schema=False)
    @app.get("/favicon.png", include_in_schema=False)
    async def favicon():
        """返回空响应，避免浏览器请求 favicon 时出现 404"""
        return Response(status_code=204)  # No Content

    # 尝试多个可能的 frontend 目录路径
    frontend_dir = None
    possible_paths = [
        Path("frontend"),  # 相对路径（开发环境）
        Path(__file__).parent.parent.parent / "frontend",  # 从 backend/app/main.py 向上查找
        Path("/var/www/geshixiugai/frontend"),  # 服务器部署路径
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            frontend_dir = path
            print(f"[Frontend] 找到前端目录: {frontend_dir}")
            break
    
    if frontend_dir:
        app.mount("/web", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
        print(f"[Frontend] 静态文件已挂载到 /web，目录: {frontend_dir}")
        
        # 添加直接路由作为备选（如果静态文件挂载失败）
        @app.get("/web/convert.html", include_in_schema=False)
        async def convert_page():
            """Word转PDF测试页面"""
            convert_file = frontend_dir / "convert.html"
            if convert_file.exists():
                return Response(
                    content=convert_file.read_text(encoding="utf-8"),
                    media_type="text/html"
                )
            raise HTTPException(status_code=404, detail="convert.html not found")
        
        # 根路径重定向到前端页面
        @app.get("/", summary="首页重定向")
        async def root():
            return RedirectResponse(url="/web")
    else:
        print("[Frontend] 警告: 未找到前端目录，尝试的路径:")
        for path in possible_paths:
            print(f"  - {path} (存在: {path.exists()})")
        # 如果没有前端文件，返回健康检查
        @app.get("/", summary="健康检查")
        async def health_check() -> dict[str, str]:
            return {"status": "ok"}

    return app


app = create_app()

