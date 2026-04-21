"""
Доменная сущность: Форма.
Хранит схему и настройки формы.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from domain.exceptions.domain_exception import DomainException


@dataclass
class FormField:
    """Value Object: Поле формы"""
    
    name: str
    field_type: str
    required: bool = False
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    VALID_TYPES = {"text", "integer", "rating", "email", "phone", "date", "checkbox"}
    
    def __post_init__(self):
        # Инвариант: тип поля должен быть валидным
        if self.field_type not in self.VALID_TYPES:
            raise DomainException(
                f"Invalid field type: {self.field_type}. Valid types: {self.VALID_TYPES}",
                code="INVALID_FIELD_TYPE"
            )
        # Инвариант: имя поля не может быть пустым
        if not self.name or not self.name.strip():
            raise DomainException(
                "Field name cannot be empty",
                code="EMPTY_FIELD_NAME"
            )


@dataclass
class AntiSpamSettings:
    """Value Object: Настройки детекции отписок"""
    
    min_filling_time_sec: int = 30
    min_comment_length: int = 3
    block_repeating_chars: bool = True
    
    def __post_init__(self):
        # Инвариант: минимальное время не может быть отрицательным
        if self.min_filling_time_sec < 0:
            raise DomainException(
                f"min_filling_time_sec cannot be negative: {self.min_filling_time_sec}",
                code="INVALID_ANTISPAM_SETTING"
            )
        # Инвариант: минимальная длина комментария не может быть отрицательной
        if self.min_comment_length < 0:
            raise DomainException(
                f"min_comment_length cannot be negative: {self.min_comment_length}",
                code="INVALID_ANTISPAM_SETTING"
            )


@dataclass
class Form:
    """Доменная модель формы"""
    
    form_id: str
    fields: List[FormField]
    anti_spam_settings: AntiSpamSettings = field(default_factory=AntiSpamSettings)
    
    def __post_init__(self):
        # Инвариант 1: форма должна содержать хотя бы одно поле
        if not self.fields:
            raise DomainException(
                "Form must have at least one field",
                code="EMPTY_FORM"
            )
        
        # Инвариант 2: имена полей должны быть уникальными
        field_names = [f.name for f in self.fields]
        duplicates = [name for name in field_names if field_names.count(name) > 1]
        if duplicates:
            raise DomainException(
                f"Duplicate field names: {set(duplicates)}",
                code="DUPLICATE_FIELD_NAMES"
            )
        
        self._fields_dict = {f.name: f for f in self.fields}
    
    def get_field(self, name: str) -> Optional[FormField]:
        """Возвращает поле по имени"""
        return self._fields_dict.get(name)
    
    def is_field_required(self, field_name: str) -> bool:
        """Проверяет, является ли поле обязательным"""
        field = self.get_field(field_name)
        return field.required if field else False
    
    def get_required_fields(self) -> List[str]:
        """Возвращает список обязательных полей"""
        return [name for name, field in self._fields_dict.items() if field.required]
    
    def get_rating_field(self) -> Optional[str]:
        """Возвращает имя поля с типом rating, если оно есть"""
        for name, field in self._fields_dict.items():
            if field.field_type == "rating":
                return name
        return None
    
    def has_rating_field(self) -> bool:
        """Проверяет, есть ли в форме поле с типом rating"""
        return self.get_rating_field() is not None
    
    def add_field(self, field: FormField) -> None:
        """Добавляет новое поле в форму"""
        # Инвариант: поле с таким именем не должно существовать
        if field.name in self._fields_dict:
            raise DomainException(
                f"Field with name '{field.name}' already exists",
                code="DUPLICATE_FIELD"
            )
        self._fields_dict[field.name] = field
        self.fields = list(self._fields_dict.values())
    
    def validate_answers(self, answers: Dict[str, Any]) -> None:
        """Валидирует ответы согласно схеме формы"""
        # Проверка обязательных полей
        for required_field in self.get_required_fields():
            if required_field not in answers or answers[required_field] is None:
                raise DomainException(
                    f"Missing required field: {required_field}",
                    code="MISSING_REQUIRED_FIELD"
                )
        
        # Проверка типов полей (упрощённая версия)
        for field_name, value in answers.items():
            field = self.get_field(field_name)
            if field and value is not None:
                self._validate_field_type(field, value)
    
    def _validate_field_type(self, field: FormField, value: Any) -> None:
        """Валидирует значение по типу поля"""
        if field.field_type == "integer":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise DomainException(
                    f"Field '{field.name}' expects integer, got {type(value).__name__}",
                    code="TYPE_MISMATCH"
                )
        elif field.field_type == "rating":
            if not isinstance(value, (int, float)) or value < 1 or value > 5:
                raise DomainException(
                    f"Field '{field.name}' expects rating 1-5, got {value}",
                    code="INVALID_RATING"
                )
        elif field.field_type == "email":
            if not isinstance(value, str) or "@" not in value:
                raise DomainException(
                    f"Field '{field.name}' expects valid email, got {value}",
                    code="INVALID_EMAIL"
                )