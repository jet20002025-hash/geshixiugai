import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from ..schemas.payments import PaymentInfo, PaymentRequest, PaymentResponse
from ..services.payment_service import PaymentService

router = APIRouter()

# 在 Vercel 上使用 /tmp 目录，本地使用 storage 目录
if os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV"):
    DOCUMENT_DIR = Path("/tmp/storage/documents")
    TEMPLATE_DIR = Path("/tmp/storage/templates")
else:
    DOCUMENT_DIR = Path("storage/documents")
    TEMPLATE_DIR = Path("storage/templates")

DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


@router.get(
    "/info/{document_id}",
    response_model=PaymentInfo,
    summary="获取支付信息",
)
async def get_payment_info(document_id: str) -> PaymentInfo:
    """获取文档的支付信息，包括价格和可用支付方式"""
    service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    try:
        info = service.get_payment_info(document_id)
        return PaymentInfo(
            document_id=info["document_id"],
            amount=info["amount"],
            currency=info["currency"],
            payment_methods=info["payment_methods"],
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")


@router.post(
    "/mock",
    response_model=PaymentResponse,
    summary="模拟支付回调，标记订单为已付费",
)
async def mock_payment(payload: PaymentRequest) -> PaymentResponse:
    """模拟支付，直接标记为已付费（用于测试）"""
    service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    try:
        metadata = service.mark_as_paid(
            document_id=payload.document_id,
            payment_method=payload.payment_method or "mock"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    return PaymentResponse(
        document_id=payload.document_id,
        paid=metadata["paid"],
        status=metadata["status"],
        payment_method=metadata.get("payment_method"),
        amount=metadata.get("payment_amount"),
        paid_at=metadata.get("paid_at"),
    )

