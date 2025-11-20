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
        print(f"[AlipayService] 私钥格式化完成，长度: {len(private_key)}, 包含BEGIN标记: {'BEGIN' in private_key}")
        
        # 处理支付宝公钥格式（确保包含BEGIN/END标记）
        public_key = self._format_public_key(self.alipay_public_key)
        print(f"[AlipayService] 公钥格式化完成，长度: {len(public_key)}, 包含BEGIN标记: {'BEGIN' in public_key}")
        
        # 初始化支付宝客户端
        try:
            self.alipay = AliPay(
                appid=self.app_id,
                app_notify_url=None,  # 在创建订单时指定
                app_private_key_string=private_key,
                alipay_public_key_string=public_key,
                sign_type=self.sign_type,
                debug=False,  # 生产环境
                config=AliPayConfig(timeout=15)
            )
            print(f"[AlipayService] 支付宝客户端初始化成功")
        except Exception as e:
            print(f"[AlipayService] 初始化支付宝客户端失败: {str(e)}")
            import traceback
            print(f"[AlipayService] 初始化错误堆栈: {traceback.format_exc()}")
            raise ValueError(f"支付宝客户端初始化失败: {str(e)}")
    
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
    
    def _format_public_key(self, key: str) -> str:
        """
        格式化支付宝公钥，确保包含BEGIN/END标记
        
        Args:
            key: 原始公钥字符串（可能没有BEGIN/END标记）
            
        Returns:
            格式化后的公钥
        """
        key = key.strip()
        
        # 如果已经有BEGIN/END标记，直接返回
        if "BEGIN PUBLIC KEY" in key or "BEGIN RSA PUBLIC KEY" in key:
            return key
        
        # 如果没有标记，添加标记
        # 支付宝公钥通常是 RSA 格式
        # 将长字符串按64字符一行格式化
        formatted_key = "\n".join([key[i:i+64] for i in range(0, len(key), 64)])
        return f"-----BEGIN PUBLIC KEY-----\n{formatted_key}\n-----END PUBLIC KEY-----"
    
    def create_payment(
        self,
        out_trade_no: str,
        total_amount: float,
        subject: str,
        return_url: str,
        notify_url: str,
        payment_type: str = "page",  # "page" 电脑网站支付, "wap" 手机网站支付
    ) -> Dict:
        """
        创建支付订单
        
        Args:
            out_trade_no: 商户订单号（使用 document_id）
            total_amount: 支付金额（元）
            subject: 订单标题
            return_url: 支付成功跳转地址
            notify_url: 支付回调地址
            payment_type: 支付类型，"page" 电脑网站支付（网页应用），"wap" 手机网站支付（移动应用）
            
        Returns:
            支付参数，包含支付URL
        """
        try:
            print(f"[AlipayService] 开始创建支付订单，订单号: {out_trade_no}, 金额: {total_amount}")
            print(f"[AlipayService] 使用网关: {self.gateway}")
            print(f"[AlipayService] AppID: {self.app_id[:4]}****" if len(self.app_id) > 4 else f"[AlipayService] AppID: {self.app_id}")
            print(f"[AlipayService] 支付类型: {payment_type} ({'电脑网站支付' if payment_type == 'page' else '手机网站支付'})")
            
            # 根据支付类型选择接口
            # 网页应用使用电脑网站支付，移动应用使用手机网站支付
            if payment_type == "page":
                # 电脑网站支付（适用于网页应用）
                order_string = self.alipay.api_alipay_trade_page_pay(
                    out_trade_no=out_trade_no,
                    total_amount=str(total_amount),
                    subject=subject,
                    return_url=return_url,
                    notify_url=notify_url,
                )
            else:
                # 手机网站支付（适用于移动应用）
                order_string = self.alipay.api_alipay_trade_wap_pay(
                    out_trade_no=out_trade_no,
                    total_amount=str(total_amount),
                    subject=subject,
                    return_url=return_url,
                    notify_url=notify_url,
                )
            
            print(f"[AlipayService] 订单字符串生成成功，长度: {len(order_string) if order_string else 0}")
            
            # 检查返回的字符串是否包含错误信息
            if order_string and ("error_response" in order_string.lower() or "code" in order_string.lower()):
                # 尝试解析错误信息
                import urllib.parse
                parsed = urllib.parse.parse_qs(order_string)
                error_info = {}
                for key, value in parsed.items():
                    if "error" in key.lower() or "code" in key.lower() or "msg" in key.lower():
                        error_info[key] = value
                
                if error_info:
                    error_msg = f"支付宝返回错误: {error_info}"
                    print(f"[AlipayService] {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                    }
            
            # 生成支付URL
            payment_url = f"{self.gateway}?{order_string}"
            
            return {
                "success": True,
                "payment_url": payment_url,
                "order_string": order_string,
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = str(e)
            print(f"[AlipayService] 创建支付订单失败: {error_msg}")
            print(f"[AlipayService] 错误堆栈: {error_trace}")
            
            # 如果是签名错误，提供更详细的提示
            if "sign" in error_msg.lower() or "签名" in error_msg or "invalid-signature" in error_msg:
                return {
                    "success": False,
                    "message": f"签名验证失败。请检查：1) 应用私钥(ALIPAY_PRIVATE_KEY)和应用公钥是否匹配（应用公钥需上传到支付宝）；2) 密钥格式是否正确（需包含BEGIN/END标记）。错误详情: {error_msg}",
                }
            
            # 如果是 ISV 权限不足错误，提供详细的解决步骤
            if "insufficient-isv-permissions" in error_msg.lower() or "isv权限不足" in error_msg or "ISV权限不足" in error_msg:
                # 根据当前使用的支付类型，提供针对性的解决方案
                current_type = "电脑网站支付" if payment_type == "page" else "手机网站支付"
                alternative_type = "手机网站支付" if payment_type == "page" else "电脑网站支付"
                
                return {
                    "success": False,
                    "message": f"ISV权限不足（当前使用{current_type}接口）。请检查：1) 应用是否已通过审核（状态应为'已上线'）；2) 是否已签约'{current_type}'产品（产品状态应为'已上线'）；3) 如果应用类型是'网页应用'，需要签约'电脑网站支付'产品；4) 如果应用类型是'移动应用'，需要签约'手机网站支付'产品。详细排查步骤请参考：支付宝ISV权限不足问题排查.md 和 支付宝网页应用接口修复说明.md。错误详情: {error_msg}",
                }
            
            return {
                "success": False,
                "message": f"创建支付订单失败: {error_msg}",
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

