from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListResponsesByFormQuery:
    """Запрос: список ответов формы"""
    
    form_id: str
    limit: int = 100
    offset: int = 0
    include_suspect: Optional[bool] = None
    
    def __post_init__(self):
        if not self.form_id or not self.form_id.strip():
            raise ValueError("form_id cannot be empty")
        if self.limit < 1 or self.limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        if self.offset < 0:
            raise ValueError("offset cannot be negative")