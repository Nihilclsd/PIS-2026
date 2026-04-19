"""
Порты — интерфейсы для взаимодействия между слоями.

- in/: входящие порты (вызываются адаптерами инфраструктуры)
- out/: исходящие порты (реализуются адаптерами инфраструктуры)
"""

from application.port.out.form_schema_repository import FormSchemaRepository
from application.port.out.response_repository import ResponseRepository
from application.port.out.geo_service import GeoService
from application.port.out.anti_spam_service import AntiSpamService, AntiSpamResult
from application.port.out.notification_service import NotificationService

__all__ = [
    "FormSchemaRepository",
    "ResponseRepository",
    "GeoService",
    "AntiSpamService",
    "AntiSpamResult",
    "NotificationService",
]