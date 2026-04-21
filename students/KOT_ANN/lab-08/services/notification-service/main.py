from fastapi import FastAPI
import threading

from services.email_service import EmailService
from services.push_service import PushService
from consumers.response_consumer import ResponseConsumer

app = FastAPI(title="Notification Service", version="1.0.0")

email_service = EmailService()
push_service = PushService()
consumer = ResponseConsumer(email_service, push_service)


@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=consumer.start_consuming, daemon=True)
    thread.start()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/notifications/email")
async def send_email(to: str, subject: str, body: str):
    return email_service.send(to, subject, body)


@app.post("/api/notifications/push")
async def send_push(user_id: str, title: str, body: str):
    return push_service.send(user_id, title, body)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)