"""
Application Layer — use-case'ы и порты.

Содержит:
- Входящие порты (in) — как внешний мир вызывает систему
- Исходящие порты (out) — как система вызывает внешний мир
- Реализацию use-case'ов (сервисы)

Зависит только от Domain Layer.
"""

from application.service.response_processor import ResponseProcessor

__all__ = ["ResponseProcessor"]