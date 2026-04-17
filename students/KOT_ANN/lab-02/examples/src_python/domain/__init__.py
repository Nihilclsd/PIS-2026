"""
Domain Layer — ядро бизнес-логики.

Содержит:
- Доменные сущности (Response, Form)
- Value Objects (FormField, AntiSpamSettings, FormAggregates)
- Доменные исключения (DomainException)

Этот слой НЕ зависит от фреймворков, БД и внешних сервисов.
"""

from domain.models.response import Response
from domain.models.form import Form, FormField, AntiSpamSettings
from domain.models.aggregate import FormAggregates
from domain.exceptions.domain_exception import DomainException

__all__ = [
    "Response",
    "Form",
    "FormField",
    "AntiSpamSettings",
    "FormAggregates",
    "DomainException",
]