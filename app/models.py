from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class ZaiaLead(BaseModel):
    whatsapp: str = Field(alias="whatsapp")
    data_evento: Optional[str] = Field(default=None, alias="data.data_evento")
    local_evento: Optional[str] = Field(default=None, alias="data.local_evento")
    tipo_evento: Optional[str] = Field(default=None, alias="data.tipo_evento")
    nome_cliente: Optional[str] = Field(default=None, alias="data.nome_lead")
    interesse_reuniao: Optional[bool] = Field(default=None, alias="data.interesse_reuniao")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class UpdateEmail(BaseModel):
    whatsapp: str
    email: EmailStr
    start_date: Optional[str] = Field(default=None, alias="action.googleCalendar.startDate")
    start_time: Optional[str] = Field(default=None, alias="action.googleCalendar.startTime")
    link_reuniao: Optional[str] = Field(default=None, alias="link reuniao")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
