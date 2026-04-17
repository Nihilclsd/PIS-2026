"""
Входящие адаптеры.

Преобразуют внешние запросы (из очереди, HTTP, gRPC) в вызовы входящих портов.
"""

from infrastructure.adapter.in.queue_consumer import QueueConsumer

__all__ = ["QueueConsumer"]
