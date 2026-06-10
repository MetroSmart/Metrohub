from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExportarReporteRequest(BaseModel):
    formato: str = Field(description="pdf | xlsx")
    usar_familia_atu: bool = True
    fecha: Optional[date] = None
    extras: dict[str, Any] = Field(default_factory=dict)

