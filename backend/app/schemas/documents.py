from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class DocumentCreateResponse(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    template_id: str = Field(..., description="模板 ID")
    status: str = Field(..., description="处理状态")
    summary: Dict[str, Any] = Field(default_factory=dict, description="修复摘要")


class DocumentDetailResponse(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    template_id: str = Field(..., description="模板 ID")
    status: str = Field(..., description="处理状态")
    paid: bool = Field(..., description="是否已付费")
    summary: Dict[str, Any] = Field(default_factory=dict, description="修复摘要")
    report_path: str = Field(..., description="修复报告路径")
    preview_path: str = Field(..., description="预览版文档路径")
    final_path: str = Field(..., description="正式版文档路径")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")


class DocumentStatusResponse(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    status: str = Field(..., description="处理状态")
    paid: bool = Field(..., description="是否已付费")

