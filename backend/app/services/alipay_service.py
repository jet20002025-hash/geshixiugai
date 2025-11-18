import os
from typing import Dict, Optional

try:
    from alipay import AliPay
    from alipay.utils import AliPayConfig
except ImportError:
    AliPay = None
    AliPayConfig = None


class AlipayService:
    """支付宝支付服务"""
    
    def __init__(self):
        self.app_id = os.getenv("ALIPAY_APP_ID", "")
        self.app_private_key = os.getenv("ALIPAY_PRIVATE_KEY", "")
        self.alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY", "")
        self.sign_type = os.getenv("ALIPAY_SIGN_TYPE", "RSA2")
        self.gateway = os.getenv("ALIPAY_GATEWAY", "https://openapi.alipay.com/gateway.do")
        
        if not AliPay:
            raise ValueError("支付宝SDK未安装，请安装 python-alipay-sdk")
        
        if not self.app_id or not self.app_private_key or not self.alipay_public_key:
            raise ValueError("支付宝配置不完整，请设置 ALIPAY_APP_ID、ALIPAY_PRIVATE_KEY 和 ALIPAY_PUBLIC_KEY 环境变量")
        
        # 处理私钥格式（确保包含BEGIN/END标记）
        private_key = self._format_private_key(self.app_private_key)
        
        # 初始化支付宝客户端
        self.alipay = AliPay(
            appid=self.app_id,
            app_notify_url=None,  # 在创建订单时指定
            app_private_key_string=private_key,
            alipay_public_key_string=self.alipay_public_key,
            sign_type=self.sign_type,
            debug=False,  # 生产环境
            config=AliPayConfig(timeout=15)
        )
    
    def _format_private_key(self, key: str) -> str:
        """
        格式化私钥，确保包含BEGIN/END标记
        
        Args:
            key: 原始私钥字符串
            
        Returns:
            格式化后的私钥
        """
        key = key.strip()
        
        # 如果已经有BEGIN/END标记，直接返回
        if "BEGIN PRIVATE KEY" in key or "BEGIN RSA PRIVATE KEY" in key:
            return key
        
        # 如果没有标记，添加标记
        # 假设是PKCS8格式（支付宝推荐）
        # 将长字符串按64字符一行格式化
        formatted_key = "\n".join([key[i:i+64] for i in range(0, len(key), 64)])
        return f"-----BEGIN PRIVATE KEY-----\n{formatted_key}\n-----END PRIVATE KEY-----"
    
    def create_payment(
        self,
        out_trade_no: str,
        total_amount: float,
        subject: str,
        return_url: str,
        notify_url: str,
    ) -> Dict:
        """
        创建支付订单（手机网站支付）
        
        Args:
            out_trade_no: 商户订单号（使用 document_id）
            total_amount: 支付金额（元）
            subject: 订单标题
            return_url: 支付成功跳转地址
            notify_url: 支付回调地址
            
        Returns:
            支付参数，包含支付URL
        """
        try:
            # 调用支付宝接口创建订单
            order_string = self.alipay.api_alipay_trade_wap_pay(
                out_trade_no=out_trade_no,
                total_amount=str(total_amount),
                subject=subject,
                return_url=return_url,
                notify_url=notify_url,
            )
            
            # 生成支付URL
            payment_url = f"{self.gateway}?{order_string}"
            
            return {
                "success": True,
                "payment_url": payment_url,
                "order_string": order_string,
            }
        except Exception as e:
            print(f"[AlipayService] 创建支付订单失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建支付订单失败: {str(e)}",
            }
    
    def verify_notify(self, data: Dict) -> bool:
        """
        验证支付回调通知
        
        Args:
            data: 支付宝回调数据（字典格式）
            
        Returns:
            True 如果验证通过
        """
        try:
            # 支付宝回调数据中，sign 字段需要单独提取
            sign = data.get("sign")
            if not sign:
                return False
            
            # 移除sign字段，验证其他字段
            data_to_verify = {k: v for k, v in data.items() if k != "sign"}
            
            # 使用支付宝SDK验证签名
            return self.alipay.verify(data_to_verify, sign)
        except Exception as e:
            print(f"[AlipayService] 验证回调签名失败: {str(e)}")
            return False

