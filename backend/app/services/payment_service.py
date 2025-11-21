import os
from datetime import datetime
from pathlib import Path

from .document_service import DocumentService


class PaymentService:
    # 默认价格（元）- 可以通过环境变量覆盖
    DEFAULT_PRICE = 9.9
    
    def __init__(self, document_dir: Path, template_dir: Path) -> None:
        self.document_dir = document_dir
        self.template_dir = template_dir

    def get_price(self) -> float:
        """获取配置的价格（从环境变量或使用默认值）"""
        price_str = os.getenv("PAYMENT_PRICE")
        if price_str:
            try:
                return float(price_str)
            except ValueError:
                pass
        return self.DEFAULT_PRICE

    def get_payment_account(self) -> dict:
        """获取收款账户信息"""
        return {
            "alipay_account": os.getenv("ALIPAY_ACCOUNT", ""),
            "wechat_account": os.getenv("WECHAT_ACCOUNT", ""),
            "bank_account": os.getenv("BANK_ACCOUNT", ""),
            "bank_name": os.getenv("BANK_NAME", ""),
            "account_name": os.getenv("ACCOUNT_NAME", ""),
        }

    def calculate_price(self, document_id: str) -> float:
        """计算文档处理价格"""
        document_service = DocumentService(document_dir=self.document_dir, template_dir=self.template_dir)
        metadata = document_service.get_document_metadata(document_id)
        if not metadata:
            raise FileNotFoundError("document not found")
        
        # 可以根据文档复杂度、页数等计算价格
        # 这里使用配置的价格
        return self.get_price()

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
        
        # 可用的支付方式（只保留模拟支付，不显示支付宝和微信）
        payment_methods = ["mock"]  # 默认只有模拟支付
        
        # 不再添加支付宝和微信支付方式
        # 如果配置了 PayJS，添加 PayJS 支付
        if os.getenv("PAYJS_MCHID") and os.getenv("PAYJS_KEY"):
            payment_methods.append("payjs")
        
        # 如果配置了其他支付方式，可以添加（但不包括支付宝和微信）
        if os.getenv("STRIPE_SECRET_KEY"):
            payment_methods.append("stripe")
        
        print(f"[PaymentService] 最终支付方式列表: {payment_methods}")
        
        payment_account = self.get_payment_account()
        
        return {
            "document_id": document_id,
            "amount": self.calculate_price(document_id),
            "currency": "CNY",
            "payment_methods": payment_methods,
            "paid": False,
            "payment_account": payment_account,
        }

    def mark_as_paid(self, document_id: str, payment_method: str = "mock") -> dict:
        """标记文档为已付费"""
        print(f"[PaymentService] mark_as_paid 调用，document_id: {document_id}, payment_method: {payment_method}")
        print(f"[PaymentService] document_dir: {self.document_dir}")
        print(f"[PaymentService] document_dir 是否存在: {self.document_dir.exists()}")
        
        document_service = DocumentService(document_dir=self.document_dir, template_dir=self.template_dir)
        metadata = document_service.get_document_metadata(document_id)
        
        print(f"[PaymentService] metadata: {metadata}")
        print(f"[PaymentService] metadata 路径: {self.document_dir / document_id / 'metadata.json'}")
        print(f"[PaymentService] metadata 文件是否存在: {(self.document_dir / document_id / 'metadata.json').exists()}")
        
        if not metadata:
            # 列出所有文档目录，用于调试
            if self.document_dir.exists():
                all_docs = [d.name for d in self.document_dir.iterdir() if d.is_dir()]
                print(f"[PaymentService] 所有文档目录: {all_docs}")
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

