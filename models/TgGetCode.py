from pydantic import BaseModel

class TgGetCode(BaseModel):
    data: str = ""