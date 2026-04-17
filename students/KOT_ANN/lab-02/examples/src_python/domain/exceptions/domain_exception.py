"""
Базовое исключение для всех доменных ошибок.
Позволяет отличать ошибки бизнес-логики от технических.
"""

class DomainException(Exception):
    """Базовое исключение доменного слоя"""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)