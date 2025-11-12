from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):
    document_id: str = Field(..., description="需要解锁的文档 ID")


class PaymentResponse(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    paid: bool = Field(..., description="是否已付费")
    status: str = Field(..., description="当前处理状态")

