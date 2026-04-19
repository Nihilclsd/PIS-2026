from dataclasses import dataclass


@dataclass(frozen=True)
class GetAggregatesQuery:
    """Запрос: получение агрегатов формы"""
    
    form_id: str
    
    def __post_init__(self):
        if not self.form_id or not self.form_id.strip():
            raise ValueError("form_id cannot be empty")