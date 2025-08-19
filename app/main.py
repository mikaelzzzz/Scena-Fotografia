import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from dotenv import load_dotenv

from .models import ZaiaLead, UpdateEmail
from .notion_service import NotionService


load_dotenv()

app = FastAPI(title="Zaia → Notion Bridge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

notion_service = NotionService()


@app.get("/")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/webhooks/zaia/lead")
async def create_or_update_lead(payload: ZaiaLead) -> dict:
    try:
        page = notion_service.create_or_update_lead(payload)
        return {"status": "success", "page_id": page.get("id")}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/zaia/lead/email")
async def update_lead_email(payload: UpdateEmail) -> dict:
    try:
        page_id = notion_service.update_email_by_whatsapp(payload.whatsapp, payload.email)
        if page_id is None:
            raise HTTPException(status_code=404, detail="Lead não encontrado para o WhatsApp informado")
        return {"status": "success", "page_id": page_id}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_port() -> int:
    try:
        return int(os.environ.get("PORT", "8000"))
    except ValueError:
        return 8000


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=get_port(), reload=False)
