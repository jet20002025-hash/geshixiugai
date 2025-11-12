import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, status

from ..schemas.templates import TemplateCreateResponse, TemplateDetailResponse
from ..services.template_service import TemplateService

router = APIRouter()

TEMPLATE_DIR = Path("storage/templates")


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

