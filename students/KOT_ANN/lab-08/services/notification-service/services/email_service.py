import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис отправки email (mock)"""
    
    def send(self, to: str, subject: str, body: str) -> dict:
        """Отправляет email"""
        logger.info(f"[MOCK] Sending email to {to}: {subject}")
        logger.info(f"Body: {body}")
        
        # В реальном приложении здесь был бы вызов SMTP или API
        return {"status": "sent", "to": to, "subject": subject}
    