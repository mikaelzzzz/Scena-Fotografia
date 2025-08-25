import os
from typing import Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from dotenv import load_dotenv
from notion_client.errors import APIResponseError

from .models import ZaiaLead, UpdateEmail
from .notion_service import NotionService
from .utils import normalize_whatsapp


load_dotenv()

app = FastAPI(title="Zaia → Notion Bridge", version="0.3.0")

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


@app.post("/debug/zaia/payload")
async def debug_zaia_payload(request: Request) -> dict:
    try:
        body: Any = await request.json()
    except Exception:
        body = None
    normalized = None
    try:
        if isinstance(body, dict) and body.get("whatsapp"):
            normalized = normalize_whatsapp(str(body.get("whatsapp")))
    except Exception:
        normalized = None
    return {"received": body, "normalized_whatsapp": normalized}


@app.get("/debug/notion/schema")
async def debug_notion_schema() -> dict:
    try:
        return notion_service.get_database_schema()
    except APIResponseError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/zaia/lead")
async def create_or_update_lead(payload: ZaiaLead) -> dict:
    try:
        page = notion_service.create_or_update_lead(payload)
        return {"status": "success", "page_id": page.get("id")}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except APIResponseError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "payload": payload.model_dump(by_alias=True),
            },
        )


@app.post("/webhooks/zaia/lead/email")
async def update_lead_email(payload: UpdateEmail) -> dict:
    try:
        page_id = notion_service.update_email_by_whatsapp(
            payload.whatsapp,
            payload.email,
            start_date=payload.start_date,
            start_time=payload.start_time,
            link_reuniao=payload.link_reuniao,
        )
        if page_id is None:
            raise HTTPException(status_code=404, detail="Lead não encontrado para o WhatsApp informado")
        return {"status": "success", "page_id": page_id}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except APIResponseError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "payload": payload.model_dump(by_alias=True),
            },
        )


def get_port() -> int:
    try:
        return int(os.environ.get("PORT", "8000"))
    except ValueError:
        return 8000


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=get_port(), reload=False)
