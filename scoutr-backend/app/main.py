from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="ScoutR API")

app.include_router(api_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
