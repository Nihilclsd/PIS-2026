from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime

from application.service.response_application_service import ResponseApplicationService
from application.command.process_response_command import ProcessResponseCommand
from application.command.reclassify_response_command import ReclassifyResponseCommand
from application.query.get_aggregates_query import GetAggregatesQuery
from application.query.get_response_by_id_query import GetResponseByIdQuery
from application.query.list_responses_by_form_query import ListResponsesByFormQuery
from application.query.dto.response_dto import ResponseDto
from application.query.dto.form_aggregates_dto import FormAggregatesDto

router = APIRouter(prefix="/api/responses", tags=["responses"])


class ResponseController:
    """REST API контроллер для работы с ответами"""

    def __init__(self, service: ResponseApplicationService):
        self.service = service

    def process_response(self, request: dict) -> dict:
        """POST /api/responses - обработать ответ"""
        command = ProcessResponseCommand(
            response_id=request.get("response_id"),
            form_id=request.get("form_id"),
            answers=request.get("answers", {}),
            ip_address=request.get("ip_address"),
            user_agent=request.get("user_agent"),
            started_at=datetime.fromisoformat(request["started_at"]),
            submitted_at=datetime.fromisoformat(request["submitted_at"])
        )
        self.service.process_response(command)
        return {"status": "accepted", "response_id": command.response_id}

    def reclassify_response(self, response_id: str, request: dict) -> dict:
        """POST /api/responses/{id}/reclassify - переклассифицировать ответ"""
        command = ReclassifyResponseCommand(
            response_id=response_id,
            quality_score=request.get("quality_score"),
            is_suspect=request.get("is_suspect"),
            suspect_reason=request.get("suspect_reason")
        )
        self.service.reclassify_response(command)
        return {"status": "reclassified", "response_id": response_id}

    def get_response(self, response_id: str) -> ResponseDto:
        """GET /api/responses/{id} - получить ответ по ID"""
        query = GetResponseByIdQuery(response_id=response_id)
        result = self.service.get_response_by_id(query)
        if not result:
            raise HTTPException(status_code=404, detail="Response not found")
        return result

    def get_aggregates(self, form_id: str) -> FormAggregatesDto:
        """GET /api/responses/aggregates/{form_id} - получить агрегаты формы"""
        query = GetAggregatesQuery(form_id=form_id)
        result = self.service.get_aggregates(query)
        if not result:
            raise HTTPException(status_code=404, detail="Form not found")
        return result

    def list_responses(
        self,
        form_id: str,
        limit: int = 100,
        offset: int = 0,
        include_suspect: Optional[bool] = None
    ) -> List[ResponseDto]:
        """GET /api/responses - список ответов формы"""
        query = ListResponsesByFormQuery(
            form_id=form_id,
            limit=limit,
            offset=offset,
            include_suspect=include_suspect
        )
        return self.service.list_responses_by_form(query)


def setup_routes(app, service):
    """Регистрирует маршруты в FastAPI приложении"""
    controller = ResponseController(service)

    @app.post("/api/responses")
    async def process_response(request: dict):
        return controller.process_response(request)

    @app.post("/api/responses/{response_id}/reclassify")
    async def reclassify_response(response_id: str, request: dict):
        return controller.reclassify_response(response_id, request)

    @app.get("/api/responses/{response_id}")
    async def get_response(response_id: str):
        return controller.get_response(response_id)

    @app.get("/api/responses/aggregates/{form_id}")
    async def get_aggregates(form_id: str):
        return controller.get_aggregates(form_id)

    @app.get("/api/responses")
    async def list_responses(
        form_id: str,
        limit: int = 100,
        offset: int = 0,
        include_suspect: bool = None
    ):
        return controller.list_responses(form_id, limit, offset, include_suspect)