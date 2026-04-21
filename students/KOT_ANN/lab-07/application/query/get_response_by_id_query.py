from dataclasses import dataclass


@dataclass(frozen=True)
class GetResponseByIdQuery:
    """Запрос: получение ответа по ID"""
    
    response_id: str
    
    def __post_init__(self):
        if not self.response_id or not self.response_id.strip():
            raise ValueError("response_id cannot be empty")