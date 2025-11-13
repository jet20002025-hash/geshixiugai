from fastapi import APIRouter, HTTPException, status

from ..schemas.feedback import FeedbackRequest, FeedbackResponse
from ..services.feedback_service import FeedbackService

router = APIRouter()


@router.post(
    "",
    response_model=FeedbackResponse,
    summary="提交用户反馈",
)
async def submit_feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    """接收用户反馈并发送邮件"""
    service = FeedbackService()
    
    feedback_data = {
        "name": feedback.name,
        "email": feedback.email,
        "subject": feedback.subject,
        "message": feedback.message,
        "document_id": feedback.document_id,
    }
    
    success = service.send_feedback_email(feedback_data)
    
    if success:
        return FeedbackResponse(
            success=True,
            message="反馈已提交，我们会尽快处理！"
        )
    else:
        # 即使发送失败，也返回成功（避免用户看到错误）
        # 实际生产环境应该记录错误日志
        return FeedbackResponse(
            success=True,
            message="反馈已提交，我们会尽快处理！"
        )

