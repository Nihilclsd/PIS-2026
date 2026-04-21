from fastapi import FastAPI
from infrastructure.config.dependency_injection import DependencyContainer
from infrastructure.adapter.driving.rest_controller import ResponseController

app = FastAPI(title="Response Processor Service", version="1.0.0")

container = DependencyContainer()
controller = ResponseController(container.get_response_application_service())

@app.post("/api/responses")
async def process_response(request: dict):
    return controller.process_response(request)

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

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)