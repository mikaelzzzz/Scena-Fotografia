from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class ZaiaLead(BaseModel):
    whatsapp: str = Field(alias="whatsapp")
    data_evento: Optional[str] = Field(default=None, alias="data evento")
    local_evento: Optional[str] = Field(default=None, alias="local evento")
    tipo_evento: Optional[str] = Field(default=None, alias="tipo evento")
    nome_cliente: Optional[str] = Field(default=None, alias="nome do cliente")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class UpdateEmail(BaseModel):
    whatsapp: str
    email: EmailStr
