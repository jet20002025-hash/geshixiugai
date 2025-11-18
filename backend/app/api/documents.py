import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse

from ..schemas.documents import (
    DocumentCreateResponse,
    DocumentDetailResponse,
    DocumentStatusResponse,
)
from ..services.document_service import DocumentService
from ..services.template_service import TemplateService
from ..utils.session_utils import get_or_create_session_id

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


# Vercel 请求体大小限制：4.5 MB
# 为了安全，我们设置 4 MB 的限制
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 MB


@router.post(
    "",
    response_model=DocumentCreateResponse,
    summary="上传待修复文档",
)
async def upload_document(request: Request, template_id: str, file: UploadFile) -> DocumentCreateResponse:
    """
    上传待修复文档，只能使用自己上传的模板
    
    注意：文件大小限制为 4 MB（Vercel 限制）
    """
    # 检查文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        file_size_mb = file.size / (1024 * 1024)
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件太大（{file_size_mb:.2f} MB），最大支持 {max_size_mb} MB。请压缩文档中的图片或删除不必要的图片后再上传。"
        )
    
    # 获取用户 session_id
    session_id = get_or_create_session_id(request)
    
    # 验证模板是否属于当前用户
    template_service = TemplateService(base_dir=TEMPLATE_DIR)
    if not template_service.is_template_owner(template_id, session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权使用此模板，只能使用自己上传的模板"
        )
    
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

    # 尝试从存储或本地获取 HTML 文件
    preview_path = Path(metadata.get("preview_path", ""))
    html_path = preview_path.with_suffix('.html') if preview_path else DOCUMENT_DIR / document_id / "preview.html"
    
    # 从存储或本地加载文件
    html_file = service._get_file_from_storage_or_local(document_id, "html", "html", html_path)
    if not html_file or not html_file.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预览文件不存在，请重新处理文档")
    
    html_content = html_file.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)


@router.get(
    "/{document_id}/download",
    summary="下载正式版文档",
)
async def download_document(document_id: str, token: str) -> FileResponse:
    """
    下载正式版文档，需要提供下载 token 验证身份
    
    Args:
        document_id: 文档ID
        token: 下载验证 token（支付成功后获取）
    """
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到文档")

    if not metadata.get("paid"):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="尚未支付，无法下载正式版")

    # 验证下载 token
    expected_token = metadata.get("download_token")
    if not expected_token or token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="下载 token 无效，请使用支付成功后获取的下载链接"
        )

    # 尝试从存储或本地获取文件
    final_path = Path(metadata.get("final_path", "")) if metadata.get("final_path") else DOCUMENT_DIR / document_id / "final.docx"
    
    # 从存储或本地加载文件
    final_file = service._get_file_from_storage_or_local(document_id, "final", "docx", final_path)
    if not final_file or not final_file.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="正式版文件不存在")

    return FileResponse(
        final_file,
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

