import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.models.response import Response
from domain.models.aggregate import FormAggregates
from infrastructure.config.database import Base
from infrastructure.adapter.out.postgres_response_repository import PostgresResponseRepository


@pytest.fixture
def db_session():
    """Создаёт временную БД для тестов"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repository(db_session):
    return PostgresResponseRepository(db_session)


@pytest.fixture
def sample_response():
    response = Response(
        response_id="RESP-123",
        form_id="FORM-42",
        answers={"name": "Иван", "rating": 5},
        started_at=datetime(2024, 1, 1, 10, 0, 0),
        submitted_at=datetime(2024, 1, 1, 10, 2, 30),
        ip_address="77.88.55.66",
        user_agent="Mozilla/5.0"
    )
    response.classify(quality_score=0.95, is_suspect=False)
    return response


class TestPostgresResponseRepository:

    def test_save_and_find_by_id(self, repository, sample_response):
        """Тест: сохранение и поиск ответа по ID"""
        repository.save(sample_response)
        
        found = repository.find_by_id("RESP-123")
        
        assert found is not None
        assert found.id == "RESP-123"
        assert found.form_id == "FORM-42"
        assert found.answers == {"name": "Иван", "rating": 5}

    def test_exists_returns_true_for_existing_response(self, repository, sample_response):
        """Тест: exists() возвращает True для существующего ответа"""
        repository.save(sample_response)
        
        assert repository.exists("RESP-123") is True

    def test_exists_returns_false_for_nonexistent_response(self, repository):
        """Тест: exists() возвращает False для несуществующего ответа"""
        assert repository.exists("RESP-NOT-FOUND") is False

    def test_find_by_form_id_returns_responses(self, repository, sample_response):
        """Тест: поиск ответов по form_id"""
        repository.save(sample_response)
        
        results = repository.find_by_form_id("FORM-42")
        
        assert len(results) == 1
        assert results[0].id == "RESP-123"

    def test_find_by_form_id_with_limit(self, repository):
        """Тест: пагинация - limit"""
        for i in range(5):
            response = Response(
                response_id=f"RESP-{i}",
                form_id="FORM-42",
                answers={},
                started_at=datetime.now(),
                submitted_at=datetime.now()
            )
            repository.save(response)
        
        results = repository.find_by_form_id("FORM-42", limit=3)
        
        assert len(results) == 3

    def test_update_aggregates_creates_new_aggregates(self, repository, sample_response):
        """Тест: update_aggregates() создаёт новые агрегаты"""
        repository.update_aggregates("FORM-42", sample_response)
        
        aggregates = repository.get_aggregates("FORM-42")
        
        assert aggregates is not None
        assert aggregates.form_id == "FORM-42"
        assert aggregates.total_responses == 1
        assert aggregates.quality_responses == 1
        assert aggregates.suspect_responses == 0

    def test_update_aggregates_updates_existing_aggregates(self, repository):
        """Тест: update_aggregates() обновляет существующие агрегаты"""
        response1 = Response(
            response_id="RESP-1",
            form_id="FORM-42",
            answers={},
            started_at=datetime.now(),
            submitted_at=datetime.now()
        )
        response1.classify(quality_score=0.95, is_suspect=False)
        
        response2 = Response(
            response_id="RESP-2",
            form_id="FORM-42",
            answers={},
            started_at=datetime.now(),
            submitted_at=datetime.now()
        )
        response2.classify(quality_score=0.15, is_suspect=True, suspect_reason="test")
        
        repository.update_aggregates("FORM-42", response1)
        repository.update_aggregates("FORM-42", response2)
        
        aggregates = repository.get_aggregates("FORM-42")
        
        assert aggregates.total_responses == 2
        assert aggregates.quality_responses == 1
        assert aggregates.suspect_responses == 1