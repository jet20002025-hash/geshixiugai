import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from ..schemas.payments import PaymentInfo, PaymentRequest, PaymentResponse
from ..services.payment_service import PaymentService

router = APIRouter()

# 在 Vercel 上使用 /tmp 目录，本地使用 storage 目录
if os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV"):
    DOCUMENT_DIR = Path("/tmp/storage/documents")
    TEMPLATE_DIR = Path("/tmp/storage/templates")
else:
    DOCUMENT_DIR = Path("storage/documents")
    TEMPLATE_DIR = Path("storage/templates")

DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


@router.get(
    "/info/{document_id}",
    response_model=PaymentInfo,
    summary="获取支付信息",
)
async def get_payment_info(document_id: str) -> PaymentInfo:
    """获取文档的支付信息，包括价格和可用支付方式"""
    service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    try:
        info = service.get_payment_info(document_id)
        from ..schemas.payments import PaymentAccount
        
        # 调试信息：检查环境变量（所有环境都记录）
        print(f"[API] 支付方式列表: {info['payment_methods']}")
        print(f"[API] WECHAT_MCH_ID 存在: {bool(os.getenv('WECHAT_MCH_ID'))}")
        print(f"[API] WECHAT_API_KEY 存在: {bool(os.getenv('WECHAT_API_KEY'))}")
        print(f"[API] WECHAT_MCH_ID 值: {os.getenv('WECHAT_MCH_ID', '')[:4]}****" if os.getenv('WECHAT_MCH_ID') else "None")
        print(f"[API] WECHAT_API_KEY 长度: {len(os.getenv('WECHAT_API_KEY', ''))}")
        
        return PaymentInfo(
            document_id=info["document_id"],
            amount=info["amount"],
            currency=info["currency"],
            payment_methods=info["payment_methods"],
            payment_account=PaymentAccount(**info["payment_account"]),
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")


@router.get(
    "/debug/config",
    summary="调试：检查支付配置",
)
async def debug_payment_config() -> dict:
    """调试端点：检查支付相关的环境变量配置"""
    config_status = {
        "wechat": {
            "mch_id_exists": bool(os.getenv("WECHAT_MCH_ID")),
            "api_key_exists": bool(os.getenv("WECHAT_API_KEY")),
            "app_id_exists": bool(os.getenv("WECHAT_APP_ID")),
            "mch_id_preview": os.getenv("WECHAT_MCH_ID", "")[:4] + "****" if os.getenv("WECHAT_MCH_ID") else None,
        },
        "payjs": {
            "mchid_exists": bool(os.getenv("PAYJS_MCHID")),
            "key_exists": bool(os.getenv("PAYJS_KEY")),
        },
        "payment_price": os.getenv("PAYMENT_PRICE", "未设置"),
        "base_url": os.getenv("BASE_URL", "未设置"),
        "vercel_env": os.getenv("VERCEL_ENV", "未设置"),
    }
    
    # 检查支付方式（与 PaymentService 逻辑一致）
    payment_methods = ["mock"]
    if os.getenv("PAYJS_MCHID") and os.getenv("PAYJS_KEY"):
        payment_methods.append("payjs")
    if os.getenv("WECHAT_MCH_ID") and os.getenv("WECHAT_API_KEY"):
        payment_methods.append("wechat")
    if os.getenv("ALIPAY_APP_ID"):
        payment_methods.append("alipay")
    
    config_status["available_payment_methods"] = payment_methods
    
    # 详细检查微信支付配置
    wechat_mch_id = os.getenv("WECHAT_MCH_ID", "")
    wechat_api_key = os.getenv("WECHAT_API_KEY", "")
    config_status["wechat"]["mch_id_length"] = len(wechat_mch_id) if wechat_mch_id else 0
    config_status["wechat"]["api_key_length"] = len(wechat_api_key) if wechat_api_key else 0
    config_status["wechat"]["configured"] = bool(wechat_mch_id and wechat_api_key)
    
    return config_status


@router.post(
    "/mock",
    response_model=PaymentResponse,
    summary="模拟支付回调，标记订单为已付费",
)
async def mock_payment(payload: PaymentRequest) -> PaymentResponse:
    """模拟支付，直接标记为已付费（用于测试）"""
    service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    try:
        metadata = service.mark_as_paid(
            document_id=payload.document_id,
            payment_method=payload.payment_method or "mock"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    return PaymentResponse(
        document_id=payload.document_id,
        paid=metadata["paid"],
        status=metadata["status"],
        payment_method=metadata.get("payment_method"),
        amount=metadata.get("payment_amount"),
        paid_at=metadata.get("paid_at"),
        download_token=metadata.get("download_token"),  # 返回下载 token
    )


@router.post(
    "/payjs/create",
    summary="创建 PayJS 支付订单",
)
async def create_payjs_payment(payload: PaymentRequest) -> dict:
    """创建 PayJS 支付订单，返回支付URL"""
    try:
        from ..services.payjs_service import PayJSService
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PayJS 配置错误: {str(e)}"
        )
    
    service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    
    # 检查文档是否存在
    try:
        amount = service.calculate_price(payload.document_id)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    
    # 获取回调地址
    base_url = os.getenv("BASE_URL", "https://geshixiugai.org")
    notify_url = f"{base_url}/payments/payjs/notify"  # 注意：没有 /api 前缀
    
    # 创建支付订单
    payjs_service = PayJSService()
    result = await payjs_service.create_payment(
        out_trade_no=payload.document_id,
        total_fee=amount,
        body=f"论文格式修复服务 - {payload.document_id[:8]}",
        notify_url=notify_url,
        attach=payload.document_id,  # 附加数据，用于回调时识别
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "创建支付订单失败")
        )
    
    return {
        "payment_url": result.get("payment_url"),
        "document_id": payload.document_id,
        "payjs_order_id": result.get("payjs_order_id"),
    }


@router.post(
    "/payjs/notify",
    summary="PayJS 支付回调",
)
async def payjs_notify(request: Request) -> JSONResponse:
    """
    处理 PayJS 支付回调通知
    
    注意：PayJS 回调使用 form-data 格式
    """
    try:
        from ..services.payjs_service import PayJSService
    except ValueError as e:
        return JSONResponse(
            status_code=500,
            content={"return_code": 0, "return_msg": f"PayJS 配置错误: {str(e)}"}
        )
    
    # 获取回调数据（form-data 格式）
    form_data = await request.form()
    data = dict(form_data)
    
    # 验证签名
    payjs_service = PayJSService()
    if not payjs_service.verify_notify(data):
        return JSONResponse(
            status_code=400,
            content={"return_code": 0, "return_msg": "签名验证失败"}
        )
    
    # 检查支付状态
    if data.get("return_code") == "1":
        # 支付成功
        document_id = data.get("out_trade_no") or data.get("attach")
        
        if document_id:
            try:
                payment_service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
                payment_service.mark_as_paid(document_id, payment_method="payjs")
            except Exception as e:
                # 记录错误但不返回错误给 PayJS（避免重复回调）
                print(f"标记订单为已支付失败: {e}")
        
        # 返回成功响应
        return JSONResponse(
            content={"return_code": 1, "return_msg": "success"}
        )
    else:
        # 支付失败
        return JSONResponse(
            content={"return_code": 0, "return_msg": "支付失败"}
        )


@router.post(
    "/wechat/create",
    summary="创建微信支付订单（H5支付）",
)
async def create_wechat_payment(payload: PaymentRequest, request: Request) -> dict:
    """创建微信支付H5支付订单，返回支付URL"""
    try:
        from ..services.wechat_pay_service import WeChatPayService
    except ValueError as e:
        print(f"[WeChat API] 导入服务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"微信支付配置错误: {str(e)}"
        )
    except Exception as e:
        print(f"[WeChat API] 导入服务异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"微信支付服务初始化失败: {str(e)}"
        )
    
    service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    
    # 检查文档是否存在
    try:
        amount = service.calculate_price(payload.document_id)
        print(f"[WeChat API] 计算价格: {amount} 元")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    
    # 获取回调地址
    base_url = os.getenv("BASE_URL", "https://geshixiugai.org")
    notify_url = f"{base_url}/payments/wechat/notify"  # 注意：没有 /api 前缀
    print(f"[WeChat API] 回调地址: {notify_url}")
    
    # 获取客户端IP
    client_ip = request.client.host if request.client else None
    print(f"[WeChat API] 客户端IP: {client_ip}")
    
    # 创建支付订单
    try:
        wechat_service = WeChatPayService()
        print(f"[WeChat API] 微信支付服务初始化成功")
        
        result = await wechat_service.create_h5_payment(
            out_trade_no=payload.document_id,
            total_fee=amount,
            body=f"论文格式修复服务 - {payload.document_id[:8]}",
            notify_url=notify_url,
            client_ip=client_ip,
        )
        
        print(f"[WeChat API] 创建支付订单结果: {result}")
        
        if not result.get("success"):
            error_msg = result.get("message", "创建支付订单失败")
            print(f"[WeChat API] 创建订单失败: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        return {
            "payment_url": result.get("payment_url"),
            "document_id": payload.document_id,
            "prepay_id": result.get("prepay_id"),
            "payment_type": result.get("payment_type", "native"),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[WeChat API] 创建支付订单异常: {str(e)}")
        import traceback
        print(f"[WeChat API] 异常堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建支付订单时发生错误: {str(e)}" if os.getenv("VERCEL_ENV") != "production" else "创建支付订单失败，请稍后重试"
        )


@router.post(
    "/wechat/notify",
    summary="微信支付回调",
)
async def wechat_notify(request: Request) -> str:
    """
    处理微信支付回调通知
    
    注意：微信支付回调使用XML格式
    """
    try:
        from ..services.wechat_pay_service import WeChatPayService
    except ValueError as e:
        # 返回XML格式的错误响应
        return f'<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[配置错误: {str(e)}]]></return_msg></xml>'
    
    # 获取回调数据（XML格式）
    xml_data = await request.body()
    xml_str = xml_data.decode("utf-8")
    
    # 验证签名并解析数据
    wechat_service = WeChatPayService()
    data = wechat_service.verify_notify(xml_str)
    
    if not data:
        # 签名验证失败
        return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名验证失败]]></return_msg></xml>'
    
    # 检查支付状态
    if data.get("return_code") == "SUCCESS" and data.get("result_code") == "SUCCESS":
        # 支付成功
        document_id = data.get("out_trade_no")
        
        if document_id:
            try:
                payment_service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
                payment_service.mark_as_paid(document_id, payment_method="wechat")
            except Exception as e:
                # 记录错误但不返回错误给微信（避免重复回调）
                print(f"标记订单为已支付失败: {e}")
        
        # 返回成功响应（XML格式）
        return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
    else:
        # 支付失败
        return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[支付失败]]></return_msg></xml>'


@router.post(
    "/alipay/create",
    summary="创建支付宝支付订单",
)
async def create_alipay_payment(payload: PaymentRequest) -> dict:
    """创建支付宝支付订单，返回支付URL"""
    try:
        from ..services.alipay_service import AlipayService
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"支付宝配置错误: {str(e)}"
        )
    except Exception as e:
        print(f"[Alipay API] 导入服务异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"支付宝服务初始化失败: {str(e)}"
        )
    
    service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
    
    # 检查文档是否存在
    try:
        amount = service.calculate_price(payload.document_id)
        print(f"[Alipay API] 计算价格: {amount} 元")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    
    # 获取回调地址
    base_url = os.getenv("BASE_URL", "https://geshixiugai.org")
    return_url = f"{base_url}/web/"  # 支付成功跳转回网站
    notify_url = f"{base_url}/payments/alipay/notify"  # 支付回调地址
    print(f"[Alipay API] 回调地址: {notify_url}")
    
    # 创建支付订单
    try:
        print(f"[Alipay API] 开始初始化支付宝服务...")
        alipay_service = AlipayService()
        print(f"[Alipay API] 支付宝服务初始化成功")
        
        print(f"[Alipay API] 准备创建支付订单，订单号: {payload.document_id}, 金额: {amount}")
        result = alipay_service.create_payment(
            out_trade_no=payload.document_id,
            total_amount=amount,
            subject=f"论文格式修复服务 - {payload.document_id[:8]}",
            return_url=return_url,
            notify_url=notify_url,
        )
        
        print(f"[Alipay API] 创建支付订单结果: success={result.get('success')}")
        
        if not result.get("success"):
            error_msg = result.get("message", "创建支付订单失败")
            print(f"[Alipay API] 创建订单失败: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg if os.getenv("VERCEL_ENV") != "production" else "创建支付订单失败，请稍后重试"
            )
        
        payment_url = result.get("payment_url")
        if not payment_url:
            print(f"[Alipay API] 警告：未获取到支付URL")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="未获取到支付链接" if os.getenv("VERCEL_ENV") != "production" else "创建支付订单失败，请稍后重试"
            )
        
        print(f"[Alipay API] 支付URL生成成功，长度: {len(payment_url)}")
        return {
            "payment_url": payment_url,
            "document_id": payload.document_id,
        }
    except HTTPException:
        raise
    except ValueError as e:
        # 配置错误
        error_msg = str(e)
        print(f"[Alipay API] 配置错误: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg if os.getenv("VERCEL_ENV") != "production" else "支付宝配置错误，请联系管理员"
        )
    except Exception as e:
        print(f"[Alipay API] 创建支付订单异常: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Alipay API] 异常堆栈: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建支付订单时发生错误: {str(e)}" if os.getenv("VERCEL_ENV") != "production" else "创建支付订单失败，请稍后重试"
        )


@router.post(
    "/alipay/notify",
    summary="支付宝支付回调",
)
async def alipay_notify(request: Request) -> str:
    """
    处理支付宝支付回调通知
    
    注意：支付宝回调使用 form-data 格式
    """
    try:
        from ..services.alipay_service import AlipayService
    except ValueError as e:
        return "fail"  # 支付宝要求返回 "fail" 表示失败
    
    # 获取回调数据（form-data 格式）
    form_data = await request.form()
    data = dict(form_data)
    
    print(f"[Alipay API] 收到支付回调: {data.get('out_trade_no')}")
    
    # 验证签名
    alipay_service = AlipayService()
    if not alipay_service.verify_notify(data):
        print(f"[Alipay API] 签名验证失败")
        return "fail"  # 支付宝要求返回 "fail" 表示失败
    
    # 检查支付状态
    trade_status = data.get("trade_status")
    if trade_status == "TRADE_SUCCESS" or trade_status == "TRADE_FINISHED":
        # 支付成功
        document_id = data.get("out_trade_no")
        
        if document_id:
            try:
                payment_service = PaymentService(document_dir=DOCUMENT_DIR, template_dir=TEMPLATE_DIR)
                payment_service.mark_as_paid(document_id, payment_method="alipay")
                print(f"[Alipay API] 订单 {document_id} 已标记为已支付")
            except Exception as e:
                # 记录错误但不返回错误给支付宝（避免重复回调）
                print(f"[Alipay API] 标记订单为已支付失败: {e}")
        
        # 返回成功响应（支付宝要求返回 "success"）
        return "success"
    else:
        # 支付失败或其他状态
        print(f"[Alipay API] 支付状态: {trade_status}")
        return "fail"

