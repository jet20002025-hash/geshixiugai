import os
import hashlib
import time
from typing import Dict, Optional
import httpx


class PayJSService:
    """PayJS 支付服务"""
    
    def __init__(self):
        self.mchid = os.getenv("PAYJS_MCHID", "")  # 商户号
        self.key = os.getenv("PAYJS_KEY", "")  # 通信密钥
        self.api_base = "https://payjs.cn/api"
        
        if not self.mchid or not self.key:
            raise ValueError("PayJS 配置不完整，请设置 PAYJS_MCHID 和 PAYJS_KEY 环境变量")
    
    def _sign(self, data: Dict) -> str:
        """
        生成 PayJS 签名
        
        Args:
            data: 需要签名的数据字典（不包含 sign 字段）
            
        Returns:
            签名字符串
        """
        # 移除空值和 sign 字段
        filtered_data = {k: v for k, v in data.items() if v and k != "sign"}
        
        # 按键名排序
        sorted_data = sorted(filtered_data.items())
        
        # 拼接字符串
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_data])
        sign_str += f"&key={self.key}"
        
        # MD5 加密并转大写
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()
        
        return sign
    
    async def create_payment(
        self,
        out_trade_no: str,
        total_fee: float,
        body: str,
        notify_url: str,
        attach: Optional[str] = None,
    ) -> Dict:
        """
        创建支付订单（收银台支付）
        
        Args:
            out_trade_no: 商户订单号（使用 document_id）
            total_fee: 支付金额（单位：分）
            body: 订单标题
            notify_url: 支付回调地址
            attach: 附加数据（可选）
            
        Returns:
            支付参数，包含支付URL
        """
        # 金额转换为分（整数）
        total_fee_cents = int(total_fee * 100)
        
        # 构造请求参数
        data = {
            "mchid": self.mchid,
            "total_fee": total_fee_cents,
            "out_trade_no": out_trade_no,
            "body": body,
            "notify_url": notify_url,
        }
        
        if attach:
            data["attach"] = attach
        
        # 生成签名
        data["sign"] = self._sign(data)
        
        # 发送请求
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/cashier",
                    data=data,
                    timeout=10.0,
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("return_code") == 1:
                    # PayJS 收银台支付返回 code_url，这是支付页面的 URL
                    payment_url = result.get("code_url") or result.get("payment_url")
                    return {
                        "success": True,
                        "payment_url": payment_url,  # 支付URL
                        "payjs_order_id": result.get("payjs_order_id"),  # PayJS订单号
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("return_msg", "创建支付订单失败"),
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求失败: {str(e)}",
            }
    
    def verify_notify(self, data: Dict) -> bool:
        """
        验证支付回调通知的签名
        
        Args:
            data: 回调数据（包含 sign 字段）
            
        Returns:
            True 如果签名验证通过
        """
        received_sign = data.get("sign", "")
        calculated_sign = self._sign(data)
        
        return received_sign == calculated_sign
    
    async def check_order(self, payjs_order_id: str) -> Dict:
        """
        查询订单状态
        
        Args:
            payjs_order_id: PayJS 订单号
            
        Returns:
            订单信息
        """
        data = {
            "payjs_order_id": payjs_order_id,
        }
        
        data["sign"] = self._sign(data)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/check",
                    data=data,
                    timeout=10.0,
                )
                response.raise_for_status()
                result = response.json()
                
                return result
        except Exception as e:
            return {
                "return_code": 0,
                "return_msg": f"查询失败: {str(e)}",
            }

