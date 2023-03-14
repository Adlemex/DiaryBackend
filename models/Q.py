from pydantic import BaseModel, Field


class Q(BaseModel):
    guid: str = ""
    date: str = ""
    froM: str = Field(alias="from", default="")
    to: str = ""