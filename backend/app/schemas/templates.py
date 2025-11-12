from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TemplateCreateResponse(BaseModel):
    template_id: str = Field(..., description="模板 ID")
    name: str = Field(..., description="模板名称")
    style_count: int = Field(..., description="解析得到的样式数量")


class TemplateDetailResponse(BaseModel):
    template_id: str = Field(..., description="模板 ID")
    name: Optional[str] = Field(None, description="模板名称")
    styles: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="样式规则集合")
    default_style: Optional[str] = Field(None, description="默认正文样式")
    created_at: Optional[datetime] = Field(None, description="创建时间")

