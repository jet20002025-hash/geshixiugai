from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class FeedbackRequest(BaseModel):
    name: Optional[str] = Field(None, description="用户姓名（可选）")
    email: Optional[EmailStr] = Field(None, description="用户邮箱（可选）")
    subject: str = Field(..., description="反馈主题")
    message: str = Field(..., min_length=10, description="反馈内容（至少10个字符）")
    document_id: Optional[str] = Field(None, description="相关文档ID（可选）")


class FeedbackResponse(BaseModel):
    success: bool = Field(..., description="是否发送成功")
    message: str = Field(..., description="响应消息")

