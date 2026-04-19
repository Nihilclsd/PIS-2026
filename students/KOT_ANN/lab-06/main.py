from fastapi import FastAPI, Depends
from infrastructure.config.dependency_injection import DependencyContainer

app = FastAPI(title="Response Processor Service", version="1.0.0")

def get_container():
    return DependencyContainer()

@app.post("/api/responses")
async def process_response(request: dict, container: DependencyContainer = Depends(get_container)):
    from infrastructure.adapter.driving.rest_controller import ResponseController
    controller = ResponseController(container.get_response_application_service())
    return controller.process_response(request)

@app.get("/api/responses/{response_id}")
async def get_response(response_id: str, container: DependencyContainer = Depends(get_container)):
    from infrastructure.adapter.driving.rest_controller import ResponseController
    controller = ResponseController(container.get_response_application_service())
    return controller.get_response(response_id)

@app.get("/api/responses/aggregates/{form_id}")
async def get_aggregates(form_id: str, container: DependencyContainer = Depends(get_container)):
    from infrastructure.adapter.driving.rest_controller import ResponseController
    controller = ResponseController(container.get_response_application_service())
    return controller.get_aggregates(form_id)

@app.get("/api/responses")
async def list_responses(
    form_id: str,
    limit: int = 100,
    offset: int = 0,
    include_suspect: bool = None,
    container: DependencyContainer = Depends(get_container)
):
    from infrastructure.adapter.driving.rest_controller import ResponseController
    controller = ResponseController(container.get_response_application_service())
    return controller.list_responses(form_id, limit, offset, include_suspect)

@app.get("/health")
async def health_check():
    return {"status": "ok"}