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
    download_token: Optional[str] = Field(None, description="下载验证 token，用于下载正式版文档")


class PaymentAccount(BaseModel):
    alipay_account: str = Field("", description="支付宝账号")
    wechat_account: str = Field("", description="微信账号")
    bank_account: str = Field("", description="银行账号")
    bank_name: str = Field("", description="银行名称")
    account_name: str = Field("", description="账户名称")


class PaymentInfo(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    amount: float = Field(..., description="支付金额（元）")
    currency: str = Field("CNY", description="货币单位")
    payment_methods: list[str] = Field(..., description="可用的支付方式")
    payment_account: PaymentAccount = Field(..., description="收款账户信息")

