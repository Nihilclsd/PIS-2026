"""
Порты — интерфейсы для взаимодействия между слоями.

- in/: входящие порты (вызываются адаптерами инфраструктуры)
- out/: исходящие порты (реализуются адаптерами инфраструктуры)
"""

# Этот файл может быть пустым или экспортировать порты
from application.port.in import ProcessResponseUseCase, ProcessResponseCommand, GetAggregatesUseCase
from application.port.out import (
    FormSchemaRepository,
    ResponseRepository,
    GeoService,
    AntiSpamService,
    AntiSpamResult,
    NotificationService,
)

__all__ = [
    "ProcessResponseUseCase",
    "ProcessResponseCommand",
    "GetAggregatesUseCase",
    "FormSchemaRepository",
    "ResponseRepository",
    "GeoService",
    "AntiSpamService",
    "AntiSpamResult",
    "NotificationService",
]