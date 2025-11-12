import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, status

from ..schemas.templates import TemplateCreateResponse, TemplateDetailResponse
from ..services.template_service import TemplateService

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


@router.post(
    "",
    response_model=TemplateCreateResponse,
    summary="上传模板并生成规则库",
)
async def upload_template(file: UploadFile) -> TemplateCreateResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 docx 模板文件，请先将模板转换为 docx 格式",
        )

    service = TemplateService(base_dir=TEMPLATE_DIR)
    template_id = await service.save_template(file)
    metadata = service.get_template_metadata(template_id)
    return TemplateCreateResponse(
        template_id=template_id,
        name=metadata.get("name", file.filename),
        style_count=len(metadata.get("styles", {})),
    )


@router.get(
    "/{template_id}",
    response_model=TemplateDetailResponse,
    summary="查看模板解析结果",
)
async def get_template(template_id: str) -> TemplateDetailResponse:
    service = TemplateService(base_dir=TEMPLATE_DIR)
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

