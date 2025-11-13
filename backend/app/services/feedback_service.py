import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict


class FeedbackService:
    # 接收反馈的邮箱
    RECIPIENT_EMAIL = "522168878@qq.com"
    
    def __init__(self):
        # 从环境变量读取 SMTP 配置（可选）
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.qq.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")  # 发送邮件的邮箱
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")  # 邮箱授权码
        self.use_smtp = bool(self.smtp_user and self.smtp_password)
    
    def send_feedback_email(self, feedback_data: Dict) -> bool:
        """发送反馈邮件"""
        try:
            # 构建邮件内容
            subject = f"【格式修改器反馈】{feedback_data.get('subject', '用户反馈')}"
            
            # 邮件正文
            body = f"""
用户反馈信息：

主题：{feedback_data.get('subject', '无')}

内容：
{feedback_data.get('message', '无')}

---
用户信息：
姓名：{feedback_data.get('name', '未提供')}
邮箱：{feedback_data.get('email', '未提供')}
文档ID：{feedback_data.get('document_id', '无')}

---
此邮件由格式修改器系统自动发送
"""
            
            # 如果配置了 SMTP，使用邮件发送
            if self.use_smtp:
                return self._send_via_smtp(subject, body)
            else:
                # 如果没有配置 SMTP，记录到日志（生产环境应该配置 SMTP）
                print(f"反馈邮件（未配置SMTP，仅记录）:\n主题: {subject}\n内容: {body}")
                return True  # 返回成功，避免用户看到错误
                
        except Exception as e:
            print(f"发送反馈邮件失败: {e}")
            return False
    
    def _send_via_smtp(self, subject: str, body: str) -> bool:
        """通过 SMTP 发送邮件"""
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.RECIPIENT_EMAIL
            msg['Subject'] = subject
            
            # 添加正文
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # 启用 TLS
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"SMTP 发送失败: {e}")
            return False

