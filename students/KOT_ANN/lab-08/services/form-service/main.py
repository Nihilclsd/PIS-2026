from fastapi import FastAPI, HTTPException
from infrastructure.config.database import get_db
from infrastructure.adapter.out.postgres_form_repository import PostgresFormRepository
from application.service.form_service import FormService
from application.command.create_form_command import CreateFormCommand
from application.query.get_form_query import GetFormQuery

app = FastAPI(title="Form Service", version="1.0.0")

def get_form_service():
    session = get_db()
    repository = PostgresFormRepository(session)
    return FormService(repository)

@app.post("/api/forms")
async def create_form(request: dict):
    command = CreateFormCommand(
        form_id=request.get("form_id"),
        fields=request.get("fields", []),
        anti_spam_settings=request.get("anti_spam_settings", {})
    )
    service = get_form_service()
    service.create_form(command)
    return {"status": "created", "form_id": command.form_id}

@app.get("/api/forms/{form_id}")
async def get_form(form_id: str):
    query = GetFormQuery(form_id=form_id)
    service = get_form_service()
    form = service.get_form(query)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form

@app.get("/health")
async def health():
    return {"status": "ok"}