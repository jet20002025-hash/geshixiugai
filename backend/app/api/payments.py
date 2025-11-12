from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from ..schemas.payments import PaymentRequest, PaymentResponse
from ..services.payment_service import PaymentService

router = APIRouter()

DOCUMENT_DIR = Path("storage/documents")


@router.post(
    "/mock",
    response_model=PaymentResponse,
    summary="模拟支付回调，标记订单为已付费",
)
async def mock_payment(payload: PaymentRequest) -> PaymentResponse:
    service = PaymentService(document_dir=DOCUMENT_DIR)
    try:
        metadata = service.mark_as_paid(document_id=payload.document_id)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    return PaymentResponse(
        document_id=payload.document_id,
        paid=metadata["paid"],
        status=metadata["status"],
    )

