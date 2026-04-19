import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.models.form import Form, FormField, AntiSpamSettings
from infrastructure.config.database import Base
from infrastructure.adapter.out.postgres_form_repository import PostgresFormRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repository(db_session):
    return PostgresFormRepository(db_session)


@pytest.fixture
def sample_form():
    fields = [
        FormField(name="name", field_type="text", required=True),
        FormField(name="rating", field_type="rating", required=True),
        FormField(name="comment", field_type="text", required=False),
    ]
    settings = AntiSpamSettings(
        min_filling_time_sec=30,
        min_comment_length=3,
        block_repeating_chars=True
    )
    return Form(form_id="FORM-42", fields=fields, anti_spam_settings=settings)


class TestPostgresFormRepository:

    def test_save_and_find_by_id(self, repository, sample_form):
        """Тест: сохранение и поиск формы по ID"""
        repository.save(sample_form)
        
        found = repository.find_by_id("FORM-42")
        
        assert found is not None
        assert found.id == "FORM-42"
        assert len(found.fields) == 3
        assert found.anti_spam_settings.min_filling_time_sec == 30

    def test_find_by_id_returns_none_for_not_found(self, repository):
        """Тест: поиск несуществующей формы возвращает None"""
        found = repository.find_by_id("FORM-NOT-FOUND")
        
        assert found is None

    def test_save_updates_existing_form(self, repository, sample_form):
        """Тест: сохранение обновляет существующую форму"""
        repository.save(sample_form)
        
        # Изменяем форму
        new_fields = [FormField(name="new_field", field_type="text", required=True)]
        updated_form = Form(form_id="FORM-42", fields=new_fields)
        repository.save(updated_form)
        
        found = repository.find_by_id("FORM-42")
        
        assert len(found.fields) == 1
        assert found.fields[0].name == "new_field"