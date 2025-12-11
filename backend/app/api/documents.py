import os
import logging
import sys
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse

# 配置日志 - 确保输出到标准错误（Gunicorn 会捕获）
logger = logging.getLogger(__name__)
# 如果 logger 还没有处理器，添加一个
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

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
async def upload_document(
    request: Request, 
    file: UploadFile,
    template_id: str = None,
    university_id: str = None
) -> DocumentCreateResponse:
    """
    上传待修复文档
    
    支持两种方式：
    1. 使用预设大学模板：提供 university_id（如 "tsinghua", "pku"）
    2. 使用自定义模板：提供 template_id（用户上传的模板）
    
    注意：template_id 和 university_id 必须二选一，不能同时提供
    
    注意：文件大小限制为 20 MB
    """
    # 验证参数
    if not template_id and not university_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供 template_id 或 university_id 之一"
        )
    if template_id and university_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能同时提供 template_id 和 university_id"
        )
    
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
    
    # 如果使用自定义模板，验证模板是否属于当前用户
    if template_id:
        session_id = get_or_create_session_id(request)
        template_service = TemplateService(base_dir=TEMPLATE_DIR)
        if not template_service.is_template_owner(template_id, session_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权使用此模板，只能使用自己上传的模板"
            )
    
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    try:
        doc_id, report = await service.process_document(
            template_id=template_id,
            university_id=university_id,
            upload=file
        )
    except FileNotFoundError as e:
        error_msg = str(e)
        if "university" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    metadata = service.get_document_metadata(doc_id)
    return DocumentCreateResponse(
        document_id=doc_id,
        template_id=template_id or f"university_{university_id}",
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

    # 准备响应数据
    response_data = metadata.copy()
    
    # 确保 template_id 不为 None（兼容旧数据）
    if not response_data.get("template_id"):
        response_data["template_id"] = "unknown"
    
    # 只在已支付时返回 download_token
    if metadata.get("paid"):
        # 确保 download_token 存在（如果不存在，从 metadata 中获取）
        if not response_data.get("download_token"):
            # 如果 metadata 中没有 token，说明可能是旧数据，保持为 None
            # 前端会处理这种情况
            print(f"[API] 警告：文档 {document_id} 已支付但缺少 download_token")
    else:
        # 未支付时不返回 token
        response_data["download_token"] = None
    
    return DocumentDetailResponse(**response_data)


@router.get(
    "/{document_id}/preview",
    summary="预览水印版（PDF优先，HTML回退）",
)
async def preview_document(document_id: str) -> Response:
    """返回PDF或HTML预览页面，用户只能查看，无法下载"""
    from fastapi.responses import FileResponse
    
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"未找到文档 {document_id}，请确认文档ID是否正确"
        )

    # 优先查找PDF预览文件
    preview_path = Path(metadata.get("preview_path", ""))
    pdf_path = preview_path.with_suffix('.pdf') if preview_path else DOCUMENT_DIR / document_id / "preview.pdf"
    html_path = preview_path.with_suffix('.html') if preview_path else DOCUMENT_DIR / document_id / "preview.html"
    
    print(f"[Preview] 查找预览文件 - PDF: {pdf_path}, HTML: {html_path}")
    print(f"[Preview] 文档元数据: {metadata.get('status', 'unknown')}")
    print(f"[Preview] 使用云存储: {service.use_storage}")
    
    # 优先返回PDF
    pdf_file = service._get_file_from_storage_or_local(document_id, "pdf", "pdf", pdf_path)
    print(f"[Preview] PDF文件查找结果: {pdf_file}, 存在: {pdf_file.exists() if pdf_file else False}")
    if pdf_file and pdf_file.exists():
        pdf_size = pdf_file.stat().st_size
        print(f"[Preview] ✅ 返回PDF预览: {pdf_file}, 大小: {pdf_size / 1024:.2f} KB")
        return FileResponse(
            path=str(pdf_file),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=preview.pdf",
                "Cache-Control": "no-cache"
            }
        )
    else:
        print(f"[Preview] ⚠️ PDF文件不存在，回退到HTML预览")
        if pdf_file:
            print(f"[Preview] PDF文件路径: {pdf_file}, 存在: {pdf_file.exists()}")
        else:
            print(f"[Preview] PDF文件查找返回None")
    
    # 回退到HTML预览
    html_file = service._get_file_from_storage_or_local(document_id, "html", "html", html_path)
    print(f"[Preview] HTML文件查找结果: {html_file}, 存在: {html_file.exists() if html_file else False}")
    
    if not html_file:
        print(f"[Preview] 预览文件不存在")
        # 检查文档状态
        doc_status = metadata.get("status", "unknown")
        if doc_status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文档尚未处理完成（状态: {doc_status}），请等待处理完成后再预览"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="预览文件不存在，请重新处理文档"
        )
    
    if not html_file.exists():
        print(f"[Preview] HTML文件路径存在但文件不存在: {html_file}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="预览文件不存在，请重新处理文档"
        )
    
    try:
        html_content = html_file.read_text(encoding="utf-8")
        print(f"[Preview] 成功加载HTML文件，大小: {len(html_content)} 字符")
        
        if not html_content or len(html_content.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="预览文件内容为空，请重新处理文档"
            )
        
        # 计算响应大小
        content_size = len(html_content.encode('utf-8'))
        print(f"[Preview] HTML内容大小: {content_size / 1024:.2f} KB")
        
        # 如果内容太大，记录警告
        if content_size > 5 * 1024 * 1024:  # 5MB
            print(f"[Preview] 警告: HTML内容较大 ({content_size / 1024 / 1024:.2f} MB)，可能影响加载速度")
        
        return HTMLResponse(
            content=html_content,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "no-cache",
                "Content-Length": str(content_size),
                "X-Content-Size-KB": str(int(content_size / 1024))
            }
        )
    except Exception as e:
        print(f"[Preview] 读取HTML文件失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取预览文件失败: {str(e)}"
        )


@router.get(
    "/{document_id}/preview-docx",
    summary="预览Word文档（直接返回DOCX文件，用于浏览器预览）",
)
async def preview_docx_document(document_id: str) -> FileResponse:
    """
    直接返回Word文档（final.docx），用于在浏览器中使用docx-preview等库预览
    这样可以避免PDF转换的格式误差
    """
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"未找到文档 {document_id}"
        )
    
    # 查找final.docx文件
    final_docx_path = DOCUMENT_DIR / document_id / "final.docx"
    docx_file = service._get_file_from_storage_or_local(document_id, "docx", "final", final_docx_path)
    
    if not docx_file or not docx_file.exists():
        # 如果final.docx不存在，尝试preview.docx
        preview_docx_path = DOCUMENT_DIR / document_id / "preview.docx"
        docx_file = service._get_file_from_storage_or_local(document_id, "docx", "preview", preview_docx_path)
    
    if not docx_file or not docx_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word文档不存在，请重新处理文档"
        )
    
    print(f"[Preview DOCX] 返回Word文档: {docx_file}, 大小: {docx_file.stat().st_size / 1024:.2f} KB")
    
    return FileResponse(
        path=str(docx_file),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": "inline; filename=preview.docx",
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",  # 允许跨域，用于前端加载
        }
    )


@router.get(
    "/{document_id}/download",
    summary="下载带水印的PDF文档",
)
async def download_document(document_id: str, token: str) -> FileResponse:
    """
    下载带水印的PDF文档，需要提供下载 token 验证身份
    
    注意：下载版和预览版是同一个带水印的PDF文件
    
    Args:
        document_id: 文档ID
        token: 下载验证 token（支付成功后获取）
    """
    from fastapi.responses import FileResponse
    
    service = DocumentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    metadata = service.get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到文档")

    if not metadata.get("paid"):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="尚未支付，无法下载文档")

    # 验证下载 token
    expected_token = metadata.get("download_token")
    if expected_token:
        # 如果有 token，必须验证
        if token != expected_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="下载 token 无效，请使用支付成功后获取的下载链接"
            )
    else:
        # 如果没有 token（可能是旧数据或特殊情况），但已支付
        # 如果 token 是 document_id（前端临时方案），允许下载
        # 这是为了兼容，确保已支付用户可以下载
        if token != document_id:
            print(f"[API] 警告：文档 {document_id} 已支付但缺少 download_token，token: {token}")
            # 允许下载（已支付状态已验证）

    # 优先返回带水印的PDF文件（与预览版相同）
    preview_path = Path(metadata.get("preview_path", "")) if metadata.get("preview_path") else DOCUMENT_DIR / document_id / "preview.pdf"
    pdf_path = preview_path.with_suffix('.pdf') if preview_path.suffix != '.pdf' else preview_path
    
    # 从存储或本地加载PDF文件
    pdf_file = service._get_file_from_storage_or_local(document_id, "pdf", "pdf", pdf_path)
    
    if pdf_file and pdf_file.exists():
        print(f"[Download] 返回带水印的PDF文件: {pdf_file}")
    return FileResponse(
            path=str(pdf_file),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{document_id}_带水印版.pdf"',
                "Cache-Control": "no-cache"
            }
        )
    
    # 如果PDF不存在，回退到HTML（转换为PDF下载）
    html_path = preview_path.with_suffix('.html') if preview_path.suffix != '.html' else preview_path
    html_file = service._get_file_from_storage_or_local(document_id, "html", "html", html_path)
    
    if html_file and html_file.exists():
        print(f"[Download] PDF不存在，返回HTML文件: {html_file}")
        return FileResponse(
            path=str(html_file),
            media_type="text/html",
            headers={
                "Content-Disposition": f'attachment; filename="{document_id}_预览版.html"',
                "Cache-Control": "no-cache"
            }
        )
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档文件不存在，请重新处理文档")


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


@router.post(
    "/convert-to-pdf",
    summary="Word转PDF测试",
)
async def convert_word_to_pdf(file: UploadFile):
    """
    将Word文档转换为PDF（使用LibreOffice）
    
    这是一个测试接口，用于验证LibreOffice转换功能
    """
    # 立即输出日志，确认函数被调用（使用多种方式确保日志能被看到）
    import sys
    log_msg = f"[Word转PDF] ========== 开始处理转换请求 =========="
    # 方式1: print 到 stderr（Gunicorn 会捕获）
    print(log_msg, file=sys.stderr, flush=True)
    # 方式2: logger
    logger.info(log_msg)
    # 方式3: 直接写入日志文件（作为备选）
    try:
        with open("/var/log/geshixiugai/error.log", "a") as f:
            f.write(f"{log_msg}\n")
    except Exception:
        pass
    
    import tempfile
    import shutil
    import uuid
    from pathlib import Path
    
    # 验证文件类型
    log_msg = f"[Word转PDF] 收到文件: {file.filename if file.filename else '未提供文件名'}"
    print(log_msg, flush=True)
    logger.info(log_msg)
    
    if not file.filename:
        log_msg = "[Word转PDF] 错误: 未提供文件名"
        print(log_msg, flush=True)
        logger.error(log_msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供文件名"
        )
    
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    log_msg = f"[Word转PDF] 文件扩展名: {file_ext}"
    print(log_msg, flush=True)
    logger.info(log_msg)
    
    if file_ext not in ['.doc', '.docx', '.odt']:
        log_msg = f"[Word转PDF] 错误: 不支持的文件类型: {file_ext}"
        print(log_msg, flush=True)
        logger.error(log_msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}，仅支持 .doc, .docx, .odt"
        )
    
    # 创建临时目录（确保权限正确）
    temp_dir = Path(tempfile.mkdtemp(prefix="word_to_pdf_"))
    # 确保临时目录权限正确（可读写执行）
    os.chmod(temp_dir, 0o755)
    temp_input = temp_dir / file.filename
    temp_pdf = temp_dir / f"{Path(file.filename).stem}.pdf"
    
    try:
        # 保存上传的文件
        with open(temp_input, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # 确保文件权限正确（可读）
        os.chmod(temp_input, 0o644)
        
        # 使用多种方式记录日志，确保能被看到
        import sys
        log_msg = f"[Word转PDF] 文件已保存到: {temp_input}"
        print(log_msg, file=sys.stderr, flush=True)
        logger.info(log_msg)
        try:
            with open("/var/log/geshixiugai/error.log", "a") as f:
                f.write(f"{log_msg}\n")
        except Exception:
            pass
        
        log_msg = f"[Word转PDF] 文件大小: {temp_input.stat().st_size} bytes"
        print(log_msg, file=sys.stderr, flush=True)
        logger.info(log_msg)
        try:
            with open("/var/log/geshixiugai/error.log", "a") as f:
                f.write(f"{log_msg}\n")
        except Exception:
            pass
        
        # 使用LibreOffice转换
        document_service = DocumentService(
            document_dir=DOCUMENT_DIR,
            template_dir=TEMPLATE_DIR
        )
        
        # 使用多种方式记录日志，确保能被看到
        import sys
        log_msg = f"[Word转PDF] 开始转换: {temp_input} -> {temp_pdf}"
        print(log_msg, file=sys.stderr, flush=True)
        logger.info(log_msg)
        try:
            with open("/var/log/geshixiugai/error.log", "a") as f:
                f.write(f"{log_msg}\n")
        except Exception:
            pass
        
        log_msg = f"[Word转PDF] 输入文件存在: {temp_input.exists()}, 大小: {temp_input.stat().st_size} bytes"
        print(log_msg, file=sys.stderr, flush=True)
        logger.info(log_msg)
        try:
            with open("/var/log/geshixiugai/error.log", "a") as f:
                f.write(f"{log_msg}\n")
        except Exception:
            pass
        
        try:
            success = document_service._try_libreoffice_pdf_conversion(
                docx_path=temp_input,
                pdf_path=temp_pdf
            )
            
            log_msg = f"[Word转PDF] 转换结果: success={success}, PDF存在: {temp_pdf.exists()}"
            print(log_msg, flush=True)
            logger.info(log_msg)
            
            if not success:
                # 收集详细的错误信息
                error_details = []
                error_details.append("PDF转换失败")
                
                # 检查LibreOffice是否可用（更详细的检查）
                import shutil
                # os 已在文件开头导入，不需要再次导入
                libreoffice_found = False
                libreoffice_path = None
                check_paths = ['/bin/libreoffice', '/bin/soffice', '/usr/bin/libreoffice', '/usr/bin/soffice']
                for path in check_paths:
                    if os.path.exists(path):
                        libreoffice_found = True
                        libreoffice_path = path
                        log_msg = f"[Word转PDF] 找到LibreOffice路径: {path}"
                        print(log_msg, flush=True)
                        logger.info(log_msg)
                        break
                
                if not libreoffice_found and not shutil.which("libreoffice") and not shutil.which("soffice"):
                    error_details.append("LibreOffice未安装")
                    error_msg = "LibreOffice未安装，请先安装LibreOffice: sudo yum install -y libreoffice-headless"
                    print(f"[Word转PDF] {error_msg}", flush=True)
                    logger.error(f"[Word转PDF] {error_msg}")
                else:
                    error_details.append(f"LibreOffice已找到: {libreoffice_path or shutil.which('libreoffice') or shutil.which('soffice')}")
                    # 检查文件是否存在
                    if not temp_input.exists():
                        error_details.append(f"输入文件不存在: {temp_input}")
                    else:
                        error_details.append(f"输入文件存在: {temp_input}")
                        try:
                            file_stat = temp_input.stat()
                            error_details.append(f"文件权限: {oct(file_stat.st_mode)}, 所有者UID: {file_stat.st_uid}")
                        except Exception as e:
                            error_details.append(f"无法获取文件权限: {e}")
                    
                    # 检查输出目录
                    if not temp_pdf.parent.exists():
                        error_details.append(f"输出目录不存在: {temp_pdf.parent}")
                    else:
                        error_details.append(f"输出目录存在: {temp_pdf.parent}")
                        try:
                            dir_stat = temp_pdf.parent.stat()
                            error_details.append(f"目录权限: {oct(dir_stat.st_mode)}, 所有者UID: {dir_stat.st_uid}")
                        except Exception as e:
                            error_details.append(f"无法获取目录权限: {e}")
                    
                    # 检查当前用户
                    try:
                        current_uid = os.getuid()
                        error_details.append(f"当前用户UID: {current_uid}")
                    except Exception as e:
                        error_details.append(f"无法获取当前用户: {e}")
                    
                    error_msg = "PDF转换失败，详细错误信息请查看服务器日志。可能的原因：1) LibreOffice权限问题 2) 文件权限问题 3) 临时目录权限问题"
                    print(f"[Word转PDF] {error_msg}", flush=True)
                    print(f"[Word转PDF] 详细诊断信息: {'; '.join(error_details)}", flush=True)
                    logger.error(f"[Word转PDF] {error_msg}")
                    logger.error(f"[Word转PDF] 详细诊断信息: {'; '.join(error_details)}")
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg + "。详细诊断信息已记录到服务器日志，请查看 /var/log/geshixiugai/error.log"
                )
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"[Word转PDF] 转换过程出现异常: {e}"
            print(error_msg, flush=True)
            import traceback
            traceback.print_exc()
            logger.exception(error_msg)
            raise
        
        if not temp_pdf.exists():
            error_msg = f"PDF转换返回成功，但文件不存在: {temp_pdf}"
            print(f"[Word转PDF] 错误: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        pdf_size = temp_pdf.stat().st_size
        print(f"[Word转PDF] PDF生成成功: {temp_pdf}, 大小: {pdf_size} bytes")
        
        if pdf_size == 0:
            error_msg = "PDF文件大小为0，转换可能失败"
            print(f"[Word转PDF] 错误: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # 读取PDF文件并返回
        def generate():
            try:
                with open(temp_pdf, "rb") as f:
                    while True:
                        chunk = f.read(8192)  # 8KB chunks
                        if not chunk:
                            break
                        yield chunk
            finally:
                    # 清理临时文件
                    try:
                        shutil.rmtree(temp_dir)
                        logger.info(f"[Word转PDF] 临时文件已清理: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"[Word转PDF] 清理临时文件失败: {e}")
        
        # 返回PDF文件流
        # 处理中文文件名编码问题：使用 RFC 5987 格式
        pdf_filename = f"{Path(file.filename).stem}.pdf"
        # 使用 quote 编码文件名，支持中文
        encoded_filename = quote(pdf_filename.encode('utf-8'))
        # 使用 RFC 5987 格式，同时提供 ASCII 和 UTF-8 版本
        content_disposition = f'attachment; filename="{pdf_filename}"; filename*=UTF-8\'\'{encoded_filename}'
        
        return StreamingResponse(
            generate(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": content_disposition
            }
        )
    
    except HTTPException:
        # 清理临时文件
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except:
            pass
        raise
    except HTTPException:
        # HTTPException 已经包含错误信息，直接重新抛出
        raise
    except Exception as e:
        error_detail = str(e)
        logger.exception(f"[Word转PDF] 转换出错: {error_detail}")
        # 清理临时文件
        try:
            if 'temp_dir' in locals() and temp_dir.exists():
                shutil.rmtree(temp_dir)
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"转换失败: {error_detail}"
        )

