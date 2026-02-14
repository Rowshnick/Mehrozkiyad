# sajil/models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class SajilInput(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    birth_date: str  # "1990-08-03" یا "1370/05/12" (ما بعداً نرمال می‌کنیم)
    birth_time: Optional[str] = None  # "14:35"
    birth_city: Optional[str] = None
    birth_country: Optional[str] = None
    gender: Optional[str] = None
    # در آینده می‌توانی فیلدهای بیشتری اضافه کنی (مثلاً timezone، زبان، هدف، ...)


class SajilResult(BaseModel):
    summary: str
    details: str
    symbols: List[str] = Field(default_factory=list)
    meta: Dict[str, str] = Field(default_factory=dict)
