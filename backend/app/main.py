import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .routers import template_router, document_router, payment_router


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

    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        app.mount("/web", StaticFiles(directory=frontend_dir, html=True), name="frontend")
        
        # 根路径重定向到前端页面
        @app.get("/", summary="首页重定向")
        async def root():
            return RedirectResponse(url="/web")
    else:
        # 如果没有前端文件，返回健康检查
        @app.get("/", summary="健康检查")
        async def health_check() -> dict[str, str]:
            return {"status": "ok"}

    return app


app = create_app()

