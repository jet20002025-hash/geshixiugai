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


# Vercel 平台限制：4.5 MB（无法通过代码修改）
# 如果文件超过 4.5MB，需要：
# 1. 配置对象存储（R2/Supabase/B2），使用预签名URL直接上传
# 2. 或压缩文件中的图片
VERCEL_LIMIT = 4.5 * 1024 * 1024  # 4.5 MB（Vercel 平台限制）
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB（代码限制，但受 Vercel 限制）


@router.post(
    "",
    response_model=DocumentCreateResponse,
    summary="上传待修复文档",
)
async def upload_document(request: Request, template_id: str, file: UploadFile) -> DocumentCreateResponse:
    """
    上传待修复文档，只能使用自己上传的模板
    
    注意：文件大小限制为 20 MB
    """
    # 检查文件大小
    if file.size and file.size > VERCEL_LIMIT:
        file_size_mb = file.size / (1024 * 1024)
        # 检查是否配置了对象存储
        from ..services.storage_factory import get_storage
        storage = get_storage()
        if storage and storage.is_available():
            # 如果配置了对象存储，提示使用直接上传
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件太大（{file_size_mb:.2f} MB），超过 Vercel 限制（4.5 MB）。系统已配置对象存储，请使用直接上传功能，或压缩文档中的图片后再上传。"
            )
        else:
            # 如果未配置对象存储，提示压缩文件
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件太大（{file_size_mb:.2f} MB），超过 Vercel 限制（4.5 MB）。请压缩文档中的图片（Word → 图片格式 → 压缩图片 → 压缩文档中的所有图片）或配置对象存储后再上传。"
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


@router.get(
    "/debug/storage",
    summary="调试：检查存储配置",
)
async def debug_storage_config() -> dict:
    """调试端点：检查存储相关的环境变量配置和可用性"""
    from ..services.storage_factory import get_storage
    from ..services.r2_storage import get_r2_storage
    from ..services.supabase_storage import get_supabase_storage
    from ..services.b2_storage import get_b2_storage
    
    # 检查 R2 配置
    r2_account_id = os.getenv("R2_ACCOUNT_ID", "")
    r2_access_key_id = os.getenv("R2_ACCESS_KEY_ID", "")
    r2_secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY", "")
    r2_bucket_name = os.getenv("R2_BUCKET_NAME", "")
    r2_endpoint = os.getenv("R2_ENDPOINT", "")
    
    # 检查 Supabase 配置
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    supabase_bucket = os.getenv("SUPABASE_BUCKET", "")
    
    # 检查 B2 配置
    b2_key_id = os.getenv("B2_KEY_ID", "")
    b2_application_key = os.getenv("B2_APPLICATION_KEY", "")
    b2_bucket_name = os.getenv("B2_BUCKET_NAME", "")
    
    # 获取存储实例并检查可用性
    storage = get_storage()
    r2_storage = get_r2_storage()
    supabase_storage = get_supabase_storage()
    b2_storage = get_b2_storage()
    
    # 构建 R2 endpoint（如果未设置但 account_id 存在）
    r2_endpoint_auto = ""
    if r2_account_id and not r2_endpoint:
        r2_endpoint_auto = f"https://{r2_account_id}.r2.cloudflarestorage.com"
    
    config_status = {
        "storage_available": storage is not None,
        "storage_type": None,
        "r2": {
            "account_id_exists": bool(r2_account_id),
            "account_id_preview": r2_account_id[:8] + "****" if r2_account_id else None,
            "access_key_id_exists": bool(r2_access_key_id),
            "access_key_id_preview": r2_access_key_id[:8] + "****" if r2_access_key_id else None,
            "secret_access_key_exists": bool(r2_secret_access_key),
            "secret_access_key_length": len(r2_secret_access_key) if r2_secret_access_key else 0,
            "bucket_name": r2_bucket_name or "未设置",
            "endpoint": r2_endpoint or r2_endpoint_auto or "未设置",
            "configured": bool(r2_access_key_id and r2_secret_access_key),
            "available": r2_storage.is_available() if r2_storage else False,
        },
        "supabase": {
            "url_exists": bool(supabase_url),
            "key_exists": bool(supabase_key),
            "bucket_exists": bool(supabase_bucket),
            "bucket_name": supabase_bucket or "未设置",
            "configured": bool(supabase_url and supabase_key and supabase_bucket),
            "available": supabase_storage.is_available() if supabase_storage else False,
        },
        "b2": {
            "key_id_exists": bool(b2_key_id),
            "application_key_exists": bool(b2_application_key),
            "bucket_name": b2_bucket_name or "未设置",
            "configured": bool(b2_key_id and b2_application_key and b2_bucket_name),
            "available": b2_storage.is_available() if b2_storage else False,
        },
        "vercel_env": os.getenv("VERCEL_ENV", "未设置"),
    }
    
    # 确定当前使用的存储类型
    if storage:
        if supabase_storage.is_available() and storage == supabase_storage:
            config_status["storage_type"] = "Supabase"
        elif b2_storage.is_available() and storage == b2_storage:
            config_status["storage_type"] = "Backblaze B2"
        elif r2_storage.is_available() and storage == r2_storage:
            config_status["storage_type"] = "Cloudflare R2"
        else:
            config_status["storage_type"] = "Unknown"
    else:
        config_status["storage_type"] = "None (使用本地文件系统)"
    
    return config_status

