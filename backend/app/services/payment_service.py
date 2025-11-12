import os
from datetime import datetime
from pathlib import Path

from .document_service import DocumentService


class PaymentService:
    # 默认价格（元）
    DEFAULT_PRICE = 9.9
    
    def __init__(self, document_dir: Path, template_dir: Path) -> None:
        self.document_dir = document_dir
        self.template_dir = template_dir

    def calculate_price(self, document_id: str) -> float:
        """计算文档处理价格"""
        document_service = DocumentService(document_dir=self.document_dir, template_dir=self.template_dir)
        metadata = document_service.get_document_metadata(document_id)
        if not metadata:
            raise FileNotFoundError("document not found")
        
        # 可以根据文档复杂度、页数等计算价格
        # 这里使用固定价格
        return self.DEFAULT_PRICE

    def get_payment_info(self, document_id: str) -> dict:
        """获取支付信息"""
        document_service = DocumentService(document_dir=self.document_dir, template_dir=self.template_dir)
        metadata = document_service.get_document_metadata(document_id)
        if not metadata:
            raise FileNotFoundError("document not found")
        
        if metadata.get("paid"):
            return {
                "document_id": document_id,
                "amount": metadata.get("payment_amount", self.DEFAULT_PRICE),
                "currency": "CNY",
                "payment_methods": [],
                "paid": True,
            }
        
        # 可用的支付方式
        payment_methods = ["mock"]  # 默认只有模拟支付
        
        # 如果配置了真实支付，添加相应方式
        if os.getenv("ALIPAY_APP_ID"):
            payment_methods.append("alipay")
        if os.getenv("WECHAT_APP_ID"):
            payment_methods.append("wechat")
        if os.getenv("STRIPE_SECRET_KEY"):
            payment_methods.append("stripe")
        
        return {
            "document_id": document_id,
            "amount": self.calculate_price(document_id),
            "currency": "CNY",
            "payment_methods": payment_methods,
            "paid": False,
        }

    def mark_as_paid(self, document_id: str, payment_method: str = "mock") -> dict:
        """标记文档为已付费"""
        document_service = DocumentService(document_dir=self.document_dir, template_dir=self.template_dir)
        metadata = document_service.get_document_metadata(document_id)
        if not metadata:
            raise FileNotFoundError("document not found")
        
        if metadata.get("paid"):
            return metadata
        
        amount = self.calculate_price(document_id)
        
        # 更新元数据
        updated_metadata = document_service.update_metadata(
            document_id,
            paid=True,
            payment_method=payment_method,
            payment_amount=amount,
            paid_at=datetime.utcnow().isoformat(),
        )
        
        return updated_metadata

