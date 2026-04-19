import pytest
from domain.models.form import Form, FormField, AntiSpamSettings
from domain.exceptions.domain_exception import DomainException


class TestFormField:
    """Юнит-тесты для Value Object FormField"""

    def test_form_field_creation_valid(self):
        field = FormField(name="email", field_type="email", required=True)
        assert field.name == "email"
        assert field.field_type == "email"

    def test_form_field_with_invalid_type_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            FormField(name="test", field_type="invalid_type")
        assert exc.value.code == "INVALID_FIELD_TYPE"

    def test_form_field_with_empty_name_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            FormField(name="", field_type="text")
        assert exc.value.code == "EMPTY_FIELD_NAME"


class TestAntiSpamSettings:
    """Юнит-тесты для Value Object AntiSpamSettings"""

    def test_default_values(self):
        settings = AntiSpamSettings()
        assert settings.min_filling_time_sec == 30
        assert settings.min_comment_length == 3

    def test_negative_filling_time_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            AntiSpamSettings(min_filling_time_sec=-10)
        assert exc.value.code == "INVALID_ANTISPAM_SETTING"


class TestForm:
    """Юнит-тесты для доменной сущности Form"""

    def setup_method(self):
        self.fields = [
            FormField(name="name", field_type="text", required=True),
            FormField(name="rating", field_type="rating", required=True),
        ]

    def test_form_creation_valid(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        assert form.form_id == "FORM-42"
        assert len(form.fields) == 2

    def test_form_without_fields_raises_exception(self):
        with pytest.raises(DomainException) as exc:
            Form(form_id="FORM-42", fields=[])
        assert exc.value.code == "EMPTY_FORM"

    def test_form_with_duplicate_field_names_raises_exception(self):
        duplicate_fields = [
            FormField(name="name", field_type="text"),
            FormField(name="name", field_type="rating"),
        ]
        with pytest.raises(DomainException) as exc:
            Form(form_id="FORM-42", fields=duplicate_fields)
        assert exc.value.code == "DUPLICATE_FIELD_NAMES"

    def test_get_field_returns_correct_field(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        field = form.get_field("rating")
        assert field is not None
        assert field.name == "rating"

    def test_get_field_returns_none_for_nonexistent(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        field = form.get_field("nonexistent")
        assert field is None

    def test_is_field_required_returns_true(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        assert form.is_field_required("name") is True

    def test_is_field_required_returns_false_for_nonexistent(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        assert form.is_field_required("nonexistent") is False

    def test_add_field_success(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        new_field = FormField(name="comment", field_type="text")
        form.add_field(new_field)
        assert form.get_field("comment") is not None
        assert len(form.fields) == 3

    def test_add_duplicate_field_raises_exception(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        duplicate = FormField(name="name", field_type="text")
        with pytest.raises(DomainException) as exc:
            form.add_field(duplicate)
        assert exc.value.code == "DUPLICATE_FIELD"

    def test_validate_answers_valid(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        answers = {"name": "Иван", "rating": 5}
        form.validate_answers(answers)  # не должно быть исключения

    def test_validate_answers_missing_required_field_raises_exception(self):
        form = Form(form_id="FORM-42", fields=self.fields)
        answers = {"name": "Иван"}
        with pytest.raises(DomainException) as exc:
            form.validate_answers(answers)
        assert exc.value.code == "MISSING_REQUIRED_FIELD"