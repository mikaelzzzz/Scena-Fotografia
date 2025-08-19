import os
from typing import Any, Dict, Optional

from notion_client import Client

from .models import ZaiaLead
from .utils import normalize_whatsapp, whatsapp_link


class NotionService:
    def __init__(self) -> None:
        self.api_key = os.environ.get("NOTION_API_KEY")
        self.database_id = os.environ.get("NOTION_DATABASE_ID")
        if not self.api_key or not self.database_id:
            raise RuntimeError("Defina NOTION_API_KEY e NOTION_DATABASE_ID nas variáveis de ambiente")

        self.client = Client(auth=self.api_key)

        self.prop_whatsapp = os.environ.get("NOTION_PROP_WHATSAPP", "WhatsApp")
        self.prop_data_evento = os.environ.get("NOTION_PROP_DATA_EVENTO", "Data do Evento")
        self.prop_local_evento = os.environ.get("NOTION_PROP_LOCAL_EVENTO", "Local do Evento")
        self.prop_tipo_servico = os.environ.get("NOTION_PROP_TIPO_SERVICO", "Tipo Serviço")
        self.prop_link_wpp = os.environ.get("NOTION_PROP_LINK_WPP", "Link Rápido WhatsApp")
        self.prop_email = os.environ.get("NOTION_PROP_EMAIL", "Email")

        self.title_prop_name = self._detect_title_property_name()

    def _detect_title_property_name(self) -> str:
        db = self.client.databases.retrieve(self.database_id)
        for name, meta in db["properties"].items():
            if meta.get("type") == "title":
                return name
        return "Name"

    def get_database_schema(self) -> Dict[str, Any]:
        db = self.client.databases.retrieve(self.database_id)
        # Return a simplified view: property name -> type
        props = {name: meta.get("type") for name, meta in db.get("properties", {}).items()}
        return {"id": db.get("id"), "title_property": self.title_prop_name, "properties": props}

    def _build_common_properties(self, *, normalized_whatsapp: str, payload: ZaiaLead) -> Dict[str, Any]:
        properties: Dict[str, Any] = {
            self.prop_whatsapp: {
                "rich_text": [
                    {"type": "text", "text": {"content": normalized_whatsapp}}
                ]
            },
            self.prop_link_wpp: {"url": whatsapp_link(normalized_whatsapp)},
        }

        if payload.data_evento:
            properties[self.prop_data_evento] = {
                "rich_text": [
                    {"type": "text", "text": {"content": payload.data_evento}}
                ]
            }
        if payload.local_evento:
            properties[self.prop_local_evento] = {
                "rich_text": [
                    {"type": "text", "text": {"content": payload.local_evento}}
                ]
            }
        if payload.tipo_evento:
            properties[self.prop_tipo_servico] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"Lead deseja: {payload.tipo_evento}"},
                    }
                ]
            }
        return properties

    def _query_page_by_whatsapp(self, normalized_whatsapp: str) -> Optional[Dict[str, Any]]:
        query = self.client.databases.query(
            database_id=self.database_id,
            filter={
                "property": self.prop_whatsapp,
                "rich_text": {"equals": normalized_whatsapp},
            },
            page_size=1,
        )
        results = query.get("results", [])
        return results[0] if results else None

    def create_or_update_lead(self, payload: ZaiaLead) -> Dict[str, Any]:
        norm = normalize_whatsapp(payload.whatsapp)
        if not norm:
            raise ValueError("WhatsApp inválido")

        existing = self._query_page_by_whatsapp(norm)
        properties = self._build_common_properties(normalized_whatsapp=norm, payload=payload)

        if existing:
            page_id = existing["id"]
            return self.client.pages.update(page_id=page_id, properties=properties)

        title_text = f"Lead {norm}"
        properties[self.title_prop_name] = {
            "title": [
                {"type": "text", "text": {"content": title_text}}
            ]
        }
        return self.client.pages.create(parent={"database_id": self.database_id}, properties=properties)

    def update_email_by_whatsapp(self, whatsapp: str, email: str) -> Optional[str]:
        norm = normalize_whatsapp(whatsapp)
        if not norm:
            return None
        existing = self._query_page_by_whatsapp(norm)
        if not existing:
            return None
        page_id = existing["id"]
        self.client.pages.update(
            page_id=page_id,
            properties={self.prop_email: {"email": email}},
        )
        return page_id
