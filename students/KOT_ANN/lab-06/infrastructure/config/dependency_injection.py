from application.service.response_application_service import ResponseApplicationService
from application.command.handler.process_response_handler import ProcessResponseHandler
from application.command.handler.reclassify_response_handler import ReclassifyResponseHandler
from application.query.handler.get_aggregates_handler import GetAggregatesHandler
from application.query.handler.get_response_by_id_handler import GetResponseByIdHandler
from application.query.handler.list_responses_by_form_handler import ListResponsesByFormHandler
from infrastructure.adapter.out.in_memory_response_repository import InMemoryResponseRepository
from infrastructure.adapter.out.in_memory_form_repository import InMemoryFormRepository
from infrastructure.adapter.out.mock_geo_service import MockGeoService
from infrastructure.adapter.out.mock_anti_spam_service import MockAntiSpamService
from infrastructure.adapter.out.mock_notification_service import MockNotificationService


class DependencyContainer:
    def __init__(self):
        self.form_repository = InMemoryFormRepository()
        self.response_repository = InMemoryResponseRepository()
        self.geo_service = MockGeoService()
        self.anti_spam_service = MockAntiSpamService()
        self.notification_service = MockNotificationService()

    def get_response_application_service(self) -> ResponseApplicationService:
        return ResponseApplicationService(
            process_response_handler=ProcessResponseHandler(
                form_repository=self.form_repository,
                response_repository=self.response_repository,
                geo_service=self.geo_service,
                anti_spam_service=self.anti_spam_service,
                notification_service=self.notification_service
            ),
            reclassify_response_handler=ReclassifyResponseHandler(
                response_repository=self.response_repository
            ),
            get_aggregates_handler=GetAggregatesHandler(
                response_repository=self.response_repository
            ),
            get_response_by_id_handler=GetResponseByIdHandler(
                response_repository=self.response_repository
            ),
            list_responses_by_form_handler=ListResponsesByFormHandler(
                response_repository=self.response_repository
            )
        )