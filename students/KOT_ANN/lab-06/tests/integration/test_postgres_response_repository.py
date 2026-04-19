import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.models.response import Response
from infrastructure.config.database import Base
from infrastructure.adapter.out.postgres_response_repository import PostgresResponseRepository


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
    """Интеграционные тесты для PostgresResponseRepository"""

    def test_save_and_find_by_id(self, repository, sample_response):
        repository.save(sample_response)
        found = repository.find_by_id("RESP-123")
        assert found is not None
        assert found.response_id == "RESP-123"
        assert found.form_id == "FORM-42"

    def test_exists_returns_true_for_existing(self, repository, sample_response):
        repository.save(sample_response)
        assert repository.exists("RESP-123") is True

    def test_exists_returns_false_for_nonexistent(self, repository):
        assert repository.exists("RESP-NOT-FOUND") is False

    def test_find_by_form_id_returns_responses(self, repository, sample_response):
        repository.save(sample_response)
        results = repository.find_by_form_id("FORM-42")
        assert len(results) == 1
        assert results[0].response_id == "RESP-123"

    def test_find_by_form_id_with_limit(self, repository):
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
        repository.update_aggregates("FORM-42", sample_response)
        aggregates = repository.get_aggregates("FORM-42")
        assert aggregates is not None
        assert aggregates.total_responses == 1
        assert aggregates.quality_responses == 1

    def test_get_aggregates_returns_none_if_not_found(self, repository):
        aggregates = repository.get_aggregates("FORM-NOT-FOUND")
        assert aggregates is None