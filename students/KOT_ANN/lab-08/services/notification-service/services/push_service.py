import logging

logger = logging.getLogger(__name__)


class PushService:
    """Сервис отправки push-уведомлений (mock)"""
    
    def send(self, user_id: str, title: str, body: str) -> dict:
        """Отправляет push-уведомление"""
        logger.info(f"[MOCK] Sending push to user {user_id}: {title}")
        logger.info(f"Body: {body}")
        
        # В реальном приложении здесь был бы вызов Firebase или APNS
        return {"status": "sent", "user_id": user_id, "title": title}