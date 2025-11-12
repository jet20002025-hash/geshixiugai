import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse

from ..schemas.documents import (
    DocumentCreateResponse,
    DocumentDetailResponse,
    DocumentStatusResponse,
)
from ..services.document_service import DocumentService

router = APIRouter()

# 在 Vercel 上使用 /tmp 目录，本地使用 storage 目录
# Vercel 会自动设置 VERCEL 环境变量
if os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV"):
    # Vercel 环境：使用 /tmp 临时目录
    DOCUMENT_DIR = Path("/tmp/storage/documents")
    TEMPLATE_DIR = Path("/tmp/storage/templates")
else:
    # 本地环境：使用项目目录
    DOCUMENT_DIR = Path("storage/documents")
    TEMPLATE_DIR = Path("storage/templates")

# 确保目录存在
DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "",
    response_model=DocumentCreateResponse,
    summary="上传待修复文档",
)
async def upload_document(template_id: str, file: UploadFile) -> DocumentCreateResponse:
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    try:
        doc_id, report = await service.process_document(template_id=template_id, upload=file)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    metadata = service.get_document_metadata(doc_id)
    return DocumentCreateResponse(
        document_id=doc_id,
        template_id=template_id,
        status=metadata["status"],
        summary=report,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="查看文档处理详情",
)
async def document_detail(document_id: str) -> DocumentDetailResponse:
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到文档")

    return DocumentDetailResponse(**metadata)


@router.get(
    "/{document_id}/preview",
    summary="网页预览水印版（仅查看，不可下载）",
)
async def preview_document(document_id: str) -> HTMLResponse:
    """返回HTML预览页面，用户只能查看，无法下载"""
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到文档")

    preview_path = Path(metadata["preview_path"])
    html_path = preview_path.with_suffix('.html')
    
    if not html_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预览文件不存在，请重新处理文档")
    
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)


@router.get(
    "/{document_id}/download",
    summary="下载正式版文档",
)
async def download_document(document_id: str) -> FileResponse:
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到文档")

    if not metadata.get("paid"):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="尚未支付，无法下载正式版")

    final_path = Path(metadata["final_path"])
    if not final_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="正式版文件不存在")

    return FileResponse(
        final_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{document_id}.docx",
    )


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="查看文档处理状态",
)
async def document_status(document_id: str) -> DocumentStatusResponse:
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到文档")

    return DocumentStatusResponse(document_id=document_id, status=metadata["status"], paid=metadata["paid"])

