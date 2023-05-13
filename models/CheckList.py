from pydantic import BaseModel

class Lesson(BaseModel):
    name: str
    done: bool

class CheckList(BaseModel):
    date: str
    uuid: str
    lessons: list[Lesson]

