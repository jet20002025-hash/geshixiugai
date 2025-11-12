from pydantic import BaseModel, Field
from typing import Optional


class PaymentRequest(BaseModel):
    document_id: str = Field(..., description="需要解锁的文档 ID")
    payment_method: Optional[str] = Field("mock", description="支付方式: mock, alipay, wechat, stripe")


class PaymentResponse(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    paid: bool = Field(..., description="是否已付费")
    status: str = Field(..., description="当前处理状态")
    payment_method: Optional[str] = Field(None, description="支付方式")
    amount: Optional[float] = Field(None, description="支付金额")
    paid_at: Optional[str] = Field(None, description="支付时间")


class PaymentInfo(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    amount: float = Field(..., description="支付金额（元）")
    currency: str = Field("CNY", description="货币单位")
    payment_methods: list[str] = Field(..., description="可用的支付方式")

