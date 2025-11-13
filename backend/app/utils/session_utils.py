import uuid
from fastapi import Request


def get_or_create_session_id(request: Request) -> str:
    """
    获取或创建用户的 session_id
    
    如果请求中有 session_id cookie，则返回它
    否则生成新的 session_id 并设置到 cookie 中
    """
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        # 生成新的 session_id
        session_id = uuid.uuid4().hex
        # 注意：这里不能直接设置 cookie，需要在响应中设置
        # 所以返回 session_id，让调用者在响应中设置 cookie
    
    return session_id


def set_session_cookie(response, session_id: str, max_age: int = 86400 * 30) -> None:
    """
    在响应中设置 session_id cookie
    
    Args:
        response: FastAPI 响应对象
        session_id: 会话ID
        max_age: Cookie 有效期（秒），默认30天
    """
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=max_age,
        httponly=True,  # 防止 XSS 攻击
        samesite="lax",  # CSRF 保护
        secure=False,  # 本地开发时设为 False，生产环境应设为 True（需要 HTTPS）
    )

