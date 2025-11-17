import hashlib
import os
import random
import string
import time
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import httpx


class WeChatPayService:
    """微信支付服务（API v2，H5支付）"""
    
    def __init__(self):
        self.mch_id = os.getenv("WECHAT_MCH_ID", "")
        self.api_key = os.getenv("WECHAT_API_KEY", "")
        self.app_id = os.getenv("WECHAT_APP_ID", "")  # 可选，H5支付需要，Native支付不需要
        self.api_base = "https://api.mch.weixin.qq.com"
        
        if not self.mch_id or not self.api_key:
            raise ValueError("微信支付配置不完整，请设置 WECHAT_MCH_ID 和 WECHAT_API_KEY 环境变量")
    
    def _generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _sign(self, data: Dict) -> str:
        """
        生成微信支付签名（MD5）
        
        Args:
            data: 需要签名的数据字典（不包含 sign 字段）
            
        Returns:
            签名字符串（大写）
        """
        # 移除空值和 sign 字段
        filtered_data = {k: v for k, v in data.items() if v and k != "sign"}
        
        # 按键名ASCII码从小到大排序
        sorted_data = sorted(filtered_data.items())
        
        # 拼接字符串
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_data])
        sign_str += f"&key={self.api_key}"
        
        # MD5 加密并转大写
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()
        
        return sign
    
    def _verify_sign(self, data: Dict) -> bool:
        """
        验证微信支付签名
        
        Args:
            data: 包含 sign 字段的数据字典
            
        Returns:
            True 如果签名验证通过
        """
        if "sign" not in data:
            return False
        
        received_sign = data["sign"]
        calculated_sign = self._sign(data)
        
        return received_sign == calculated_sign
    
    def _dict_to_xml(self, data: Dict) -> str:
        """将字典转换为XML字符串"""
        xml = "<xml>"
        for k, v in data.items():
            xml += f"<{k}><![CDATA[{v}]]></{k}>"
        xml += "</xml>"
        return xml
    
    def _xml_to_dict(self, xml_str: str) -> Dict:
        """将XML字符串转换为字典"""
        root = ET.fromstring(xml_str)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result
    
    async def create_h5_payment(
        self,
        out_trade_no: str,
        total_fee: float,
        body: str,
        notify_url: str,
        client_ip: Optional[str] = None,
    ) -> Dict:
        """
        创建H5支付订单
        
        Args:
            out_trade_no: 商户订单号（使用 document_id）
            total_fee: 支付金额（元）
            body: 商品描述
            notify_url: 支付回调地址
            client_ip: 用户IP地址（可选）
            
        Returns:
            支付参数，包含支付URL
        """
        # 金额转换为分（整数）
        total_fee_cents = int(total_fee * 100)
        
        # 微信支付API v2要求必须有appid（无论是H5支付还是Native支付）
        # 如果没有配置appid，无法创建支付订单
        if not self.app_id:
            return {
                "success": False,
                "message": "未配置WECHAT_APP_ID。请参考以下方式获取：1) 注册微信公众平台获取公众号AppID；2) 或注册微信开放平台创建移动应用获取AppID。Native支付（扫码支付）和H5支付都需要AppID。",
            }
        
        # 判断使用H5支付还是Native支付
        # H5支付需要scene_info，Native支付不需要
        use_h5 = True  # 默认使用H5支付，用户体验更好
        trade_type = "MWEB" if use_h5 else "NATIVE"
        
        # 构造请求参数
        data = {
            "appid": self.app_id,  # 必须配置appid
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "body": body,
            "out_trade_no": out_trade_no,
            "total_fee": str(total_fee_cents),
            "spbill_create_ip": client_ip or "127.0.0.1",
            "notify_url": notify_url,
            "trade_type": trade_type,
        }
        
        # H5支付需要scene_info
        if use_h5:
            data["scene_info"] = '{"h5_info": {"type":"Wap","wap_url":"https://geshixiugai.org","wap_name":"论文格式修复"}}'
        
        # 生成签名
        data["sign"] = self._sign(data)
        
        # 转换为XML
        xml_data = self._dict_to_xml(data)
        
        # 发送请求
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/pay/unifiedorder",
                    content=xml_data.encode("utf-8"),
                    headers={"Content-Type": "application/xml"},
                    timeout=10.0,
                )
                response.raise_for_status()
                
                # 解析响应
                result = self._xml_to_dict(response.text)
                
                if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                    # 支付成功，返回支付URL
                    if trade_type == "MWEB":
                        # H5支付返回mweb_url
                        mweb_url = result.get("mweb_url")
                        if mweb_url:
                            return {
                                "success": True,
                                "payment_url": mweb_url,
                                "prepay_id": result.get("prepay_id"),
                                "payment_type": "h5",
                            }
                        else:
                            return {
                                "success": False,
                                "message": "未获取到支付URL",
                            }
                    else:
                        # Native支付返回code_url（二维码）
                        code_url = result.get("code_url")
                        if code_url:
                            return {
                                "success": True,
                                "payment_url": code_url,
                                "prepay_id": result.get("prepay_id"),
                                "payment_type": "native",  # 扫码支付
                            }
                        else:
                            return {
                                "success": False,
                                "message": "未获取到支付二维码",
                            }
                else:
                    return {
                        "success": False,
                        "message": result.get("err_code_des") or result.get("return_msg", "创建支付订单失败"),
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求失败: {str(e)}",
            }
    
    def verify_notify(self, xml_data: str) -> Optional[Dict]:
        """
        验证支付回调通知
        
        Args:
            xml_data: 回调XML数据
            
        Returns:
            解析后的数据字典，如果验证失败返回None
        """
        try:
            data = self._xml_to_dict(xml_data)
            
            # 验证签名
            if not self._verify_sign(data):
                return None
            
            return data
        except Exception:
            return None

