from infrastructure.adapter.out.postgres_response_repository import PostgresResponseRepository
from infrastructure.adapter.out.real_geo_service import RealGeoService
from infrastructure.adapter.out.mock_anti_spam_service import MockAntiSpamService
from infrastructure.adapter.out.mock_notification_service import MockNotificationService
from infrastructure.config.database import SessionLocal


class DependencyContainer:
    def __init__(self):
        # Сессия БД
        self.db_session = SessionLocal()

        # Исходящие адаптеры (реальные)
        self.response_repository = PostgresResponseRepository(self.db_session)
        self.geo_service = RealGeoService()
        self.anti_spam_service = MockAntiSpamService()  # пока mock
        self.notification_service = MockNotificationService()  # пока mock

        # TODO: добавить FormSchemaRepository (аналогично ResponseRepository)

    def get_response_repository(self):
        return self.response_repository

    def get_geo_service(self):
        return self.geo_service

    def get_anti_spam_service(self):
        return self.anti_spam_service

    def get_notification_service(self):
        return self.notification_service

    def close(self):
        self.db_session.close()