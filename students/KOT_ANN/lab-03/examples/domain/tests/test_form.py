import pytest
from domain.models.form import Form, FormField, AntiSpamSettings
from domain.exceptions.domain_exception import DomainException


class TestFormField:
    """Тесты для Value Object FormField"""
    
    def test_form_field_creation_valid(self):
        """Тест: создание валидного поля формы"""
        field = FormField(name="email", field_type="email", required=True)
        assert field.name == "email"
        assert field.field_type == "email"
        assert field.required is True
    
    def test_form_field_with_invalid_type_raises_exception(self):
        """Тест: поле с невалидным типом вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            FormField(name="test", field_type="invalid_type")
        assert exc_info.value.code == "INVALID_FIELD_TYPE"
    
    def test_form_field_with_empty_name_raises_exception(self):
        """Тест: поле с пустым именем вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            FormField(name="", field_type="text")
        assert exc_info.value.code == "EMPTY_FIELD_NAME"
    
    def test_form_field_with_whitespace_name_raises_exception(self):
        """Тест: поле с именем из пробелов вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            FormField(name="   ", field_type="text")
        assert exc_info.value.code == "EMPTY_FIELD_NAME"


class TestAntiSpamSettings:
    """Тесты для Value Object AntiSpamSettings"""
    
    def test_anti_spam_settings_default_values(self):
        """Тест: настройки антиспама со значениями по умолчанию"""
        settings = AntiSpamSettings()
        assert settings.min_filling_time_sec == 30
        assert settings.min_comment_length == 3
        assert settings.block_repeating_chars is True
    
    def test_anti_spam_settings_custom_values(self):
        """Тест: настройки антиспама с пользовательскими значениями"""
        settings = AntiSpamSettings(
            min_filling_time_sec=60,
            min_comment_length=10,
            block_repeating_chars=False
        )
        assert settings.min_filling_time_sec == 60
        assert settings.min_comment_length == 10
        assert settings.block_repeating_chars is False
    
    def test_anti_spam_settings_negative_filling_time_raises_exception(self):
        """Тест: отрицательное min_filling_time_sec вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            AntiSpamSettings(min_filling_time_sec=-10)
        assert exc_info.value.code == "INVALID_ANTISPAM_SETTING"
    
    def test_anti_spam_settings_negative_comment_length_raises_exception(self):
        """Тест: отрицательное min_comment_length вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            AntiSpamSettings(min_comment_length=-5)
        assert exc_info.value.code == "INVALID_ANTISPAM_SETTING"


class TestForm:
    """Тесты для доменной модели Form"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        self.fields = [
            FormField(name="name", field_type="text", required=True),
            FormField(name="rating", field_type="rating", required=True),
            FormField(name="comment", field_type="text", required=False),
        ]
        self.form_id = "FORM-42"
    
    def test_form_creation_valid(self):
        """Тест: создание валидной формы"""
        form = Form(form_id=self.form_id, fields=self.fields)
        assert form.form_id == self.form_id
        assert len(form.fields) == 3
        assert form.get_field("name") is not None
        assert form.get_field("rating") is not None
        assert form.get_field("comment") is not None
    
    def test_form_without_fields_raises_exception(self):
        """Тест: форма без полей вызывает исключение"""
        with pytest.raises(DomainException) as exc_info:
            Form(form_id=self.form_id, fields=[])
        assert exc_info.value.code == "EMPTY_FORM"
    
    def test_form_with_duplicate_field_names_raises_exception(self):
        """Тест: форма с дублирующимися именами полей вызывает исключение"""
        fields = [
            FormField(name="name", field_type="text"),
            FormField(name="name", field_type="rating"),  # дубликат
        ]
        with pytest.raises(DomainException) as exc_info:
            Form(form_id=self.form_id, fields=fields)
        assert exc_info.value.code == "DUPLICATE_FIELD_NAMES"
    
    def test_get_field_returns_correct_field(self):
        """Тест: get_field() возвращает правильное поле"""
        form = Form(form_id=self.form_id, fields=self.fields)
        field = form.get_field("rating")
        assert field is not None
        assert field.name == "rating"
        assert field.field_type == "rating"
    
    def test_get_field_returns_none_for_nonexistent_field(self):
        """Тест: get_field() возвращает None для несуществующего поля"""
        form = Form(form_id=self.form_id, fields=self.fields)
        field = form.get_field("nonexistent")
        assert field is None
    
    def test_is_field_required_returns_true_for_required_field(self):
        """Тест: is_field_required() возвращает True для обязательного поля"""
        form = Form(form_id=self.form_id, fields=self.fields)
        assert form.is_field_required("name") is True
        assert form.is_field_required("rating") is True
    
    def test_is_field_required_returns_false_for_optional_field(self):
        """Тест: is_field_required() возвращает False для необязательного поля"""
        form = Form(form_id=self.form_id, fields=self.fields)
        assert form.is_field_required("comment") is False
    
    def test_is_field_required_returns_false_for_nonexistent_field(self):
        """Тест: is_field_required() возвращает False для несуществующего поля"""
        form = Form(form_id=self.form_id, fields=self.fields)
        assert form.is_field_required("nonexistent") is False
    
    def test_get_required_fields_returns_list_of_required_field_names(self):
        """Тест: get_required_fields() возвращает список обязательных полей"""
        form = Form(form_id=self.form_id, fields=self.fields)
        required = form.get_required_fields()
        assert "name" in required
        assert "rating" in required
        assert "comment" not in required
    
    def test_get_rating_field_returns_rating_field_name(self):
        """Тест: get_rating_field() возвращает имя поля с типом rating"""
        form = Form(form_id=self.form_id, fields=self.fields)
        assert form.get_rating_field() == "rating"
    
    def test_get_rating_field_returns_none_if_no_rating_field(self):
        """Тест: get_rating_field() возвращает None, если нет поля с типом rating"""
        fields = [FormField(name="name", field_type="text")]
        form = Form(form_id=self.form_id, fields=fields)
        assert form.get_rating_field() is None
    
    def test_has_rating_field_returns_true_if_rating_field_exists(self):
        """Тест: has_rating_field() возвращает True, если есть поле rating"""
        form = Form(form_id=self.form_id, fields=self.fields)
        assert form.has_rating_field() is True
    
    def test_has_rating_field_returns_false_if_no_rating_field(self):
        """Тест: has_rating_field() возвращает False, если нет поля rating"""
        fields = [FormField(name="name", field_type="text")]
        form = Form(form_id=self.form_id, fields=fields)
        assert form.has_rating_field() is False
    
    def test_add_field_success(self):
        """Тест: добавление нового поля в форму"""
        form = Form(form_id=self.form_id, fields=self.fields)
        new_field = FormField(name="new_field", field_type="text")
        form.add_field(new_field)
        assert form.get_field("new_field") is not None
        assert len(form.fields) == 4
    
    def test_add_duplicate_field_raises_exception(self):
        """Тест: добавление дублирующегося поля вызывает исключение"""
        form = Form(form_id=self.form_id, fields=self.fields)
        duplicate = FormField(name="name", field_type="text")
        with pytest.raises(DomainException) as exc_info:
            form.add_field(duplicate)
        assert exc_info.value.code == "DUPLICATE_FIELD"
    
    def test_validate_answers_valid(self):
        """Тест: валидация корректных ответов"""
        form = Form(form_id=self.form_id, fields=self.fields)
        answers = {"name": "Иван", "rating": 5, "comment": "Хорошо"}
        form.validate_answers(answers)  # не должно быть исключения
    
    def test_validate_answers_missing_required_field_raises_exception(self):
        """Тест: отсутствие обязательного поля вызывает исключение"""
        form = Form(form_id=self.form_id, fields=self.fields)
        answers = {"name": "Иван"}  # нет rating
        with pytest.raises(DomainException) as exc_info:
            form.validate_answers(answers)
        assert exc_info.value.code == "MISSING_REQUIRED_FIELD"
    
    def test_validate_answers_invalid_rating_raises_exception(self):
        """Тест: неверное значение rating вызывает исключение"""
        form = Form(form_id=self.form_id, fields=self.fields)
        answers = {"name": "Иван", "rating": 10, "comment": "Хорошо"}
        with pytest.raises(DomainException) as exc_info:
            form.validate_answers(answers)
        assert exc_info.value.code == "INVALID_RATING"
    
    def test_validate_answers_invalid_email_raises_exception(self):
        """Тест: неверный email вызывает исключение"""
        fields = [FormField(name="email", field_type="email", required=True)]
        form = Form(form_id=self.form_id, fields=fields)
        answers = {"email": "not-an-email"}
        with pytest.raises(DomainException) as exc_info:
            form.validate_answers(answers)
        assert exc_info.value.code == "INVALID_EMAIL"