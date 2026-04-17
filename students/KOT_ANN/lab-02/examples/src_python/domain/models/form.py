"""
Доменная сущность: Форма.
Хранит схему и настройки формы.
"""

from typing import List, Dict, Any, Optional


class FormField:
    """Value Object: Поле формы"""
    
    def __init__(
        self,
        name: str,
        field_type: str,
        required: bool = False,
        constraints: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.field_type = field_type  # text, integer, rating, etc.
        self.required = required
        self.constraints = constraints or {}


class AntiSpamSettings:
    """Value Object: Настройки детекции отписок"""
    
    def __init__(
        self,
        min_filling_time_sec: int = 30,
        min_comment_length: int = 3,
        block_repeating_chars: bool = True
    ):
        self.min_filling_time_sec = min_filling_time_sec
        self.min_comment_length = min_comment_length
        self.block_repeating_chars = block_repeating_chars


class Form:
    """Доменная модель формы"""
    
    def __init__(
        self,
        form_id: str,
        fields: List[FormField],
        anti_spam_settings: Optional[AntiSpamSettings] = None
    ):
        self.id = form_id
        self.fields = {f.name: f for f in fields}
        self.anti_spam_settings = anti_spam_settings or AntiSpamSettings()
    
    def get_field(self, name: str) -> Optional[FormField]:
        """Возвращает поле по имени"""
        return self.fields.get(name)
    
    def is_field_required(self, field_name: str) -> bool:
        """Проверяет, является ли поле обязательным"""
        field = self.get_field(field_name)
        return field.required if field else False