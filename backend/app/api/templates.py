import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, UploadFile, status

from ..schemas.templates import TemplateCreateResponse, TemplateDetailResponse
from ..services.template_service import TemplateService
from ..utils.session_utils import get_or_create_session_id, set_session_cookie

router = APIRouter()

# 在 Vercel 上使用 /tmp 目录，本地使用 storage 目录
# Vercel 会自动设置 VERCEL 环境变量
if os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV"):
    # Vercel 环境：使用 /tmp 临时目录
    TEMPLATE_DIR = Path("/tmp/storage/templates")
else:
    # 本地环境：使用项目目录
    TEMPLATE_DIR = Path("storage/templates")

# 确保目录存在
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Vercel 请求体大小限制：4.5 MB
# 为了安全，我们设置 4 MB 的限制
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 MB


@router.post(
    "",
    response_model=TemplateCreateResponse,
    summary="上传模板并生成规则库",
)
async def upload_template(request: Request, response: Response, file: UploadFile) -> TemplateCreateResponse:
    """
    上传模板并生成规则库，模板与当前用户（session）关联
    
    注意：文件大小限制为 4 MB（Vercel 限制）
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 docx 模板文件，请先将模板转换为 docx 格式",
        )
    
    # 检查文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        file_size_mb = file.size / (1024 * 1024)
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件太大（{file_size_mb:.2f} MB），最大支持 {max_size_mb} MB。请压缩文档中的图片或删除不必要的图片后再上传。"
        )

    # 获取或创建用户 session_id
    session_id = get_or_create_session_id(request)
    
    service = TemplateService(base_dir=TEMPLATE_DIR)
    template_id = await service.save_template(file, session_id=session_id)
    metadata = service.get_template_metadata(template_id)
    
    # 设置 session cookie（如果是新创建的）
    if not request.cookies.get("session_id"):
        set_session_cookie(response, session_id)
    
    return TemplateCreateResponse(
        template_id=template_id,
        name=metadata.get("name", file.filename),
        style_count=len(metadata.get("styles", {})),
    )


@router.get(
    "",
    summary="获取当前用户的所有模板列表",
)
async def list_user_templates(request: Request) -> list[dict]:
    """
    获取当前用户的所有模板列表
    """
    session_id = get_or_create_session_id(request)
    service = TemplateService(base_dir=TEMPLATE_DIR)
    templates = service.get_user_templates(session_id)
    return templates


@router.get(
    "/{template_id}",
    response_model=TemplateDetailResponse,
    summary="查看模板解析结果",
)
async def get_template(request: Request, template_id: str) -> TemplateDetailResponse:
    """
    查看模板解析结果，只能查看自己上传的模板
    """
    session_id = get_or_create_session_id(request)
    service = TemplateService(base_dir=TEMPLATE_DIR)
    
    # 验证模板是否属于当前用户
    if not service.is_template_owner(template_id, session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此模板，只能访问自己上传的模板"
        )
    
    metadata = service.get_template_metadata(template_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到对应模板")

    return TemplateDetailResponse(
        template_id=template_id,
        name=metadata.get("name"),
        styles=metadata.get("styles", {}),
        default_style=metadata.get("default_style"),
        created_at=metadata.get("created_at"),
    )

