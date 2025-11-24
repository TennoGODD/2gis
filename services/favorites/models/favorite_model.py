from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class FavoriteModel(BaseModel):
    id: int
    title: str
    lat: float
    lon: float
    color: Optional[str] = None
    created_at: str

    @validator('created_at')
    def validate_iso_format(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError(f'Invalid ISO format: {v}')

    def __str__(self):
        return f"Favorite(id={self.id}, title='{self.title}', lat={self.lat}, lon={self.lon})"