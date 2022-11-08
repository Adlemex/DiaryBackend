import os
from datetime import datetime

import http3
from fastapi import FastAPI, UploadFile, File
from fastapi.openapi.models import Response
from http3 import Headers
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from pydantic import BaseModel, Field


class Q(BaseModel):
    guid: str = "DDFED2B991D7AEE62D9A8136AD98B737"
    date: str = ""
    froM: str = Field(alias="from", default="")
    to: str = ""


tags_metadata = [
    {
        "name": "images",
        "description": "Получить иконку для раздела сообщений",
    },
    {
        "name": "diaryday",
        "description": "Один день из дневника",
    },
    {
        "name": "periodmarks",
        "description": "Я не знаю что это такое, но официальное приложение зачем-то обращается сюда",
    },
    {
        "name": "allperiods",
        "description": "Четверти или другие периоды",
    },
    {
        "name": "marksbyperiod",
        "description": "Оценки с периода from до to",
    },
    {
        "name": "All Marks",
        "description": "Все оценки",
    },
]

app = FastAPI(title="PskoveduAPI", description="Прокси для api pskovedu", tags_metadata=tags_metadata)
client = http3.AsyncClient()
base_url = "http://213.145.5.42:8090"
apikey = "Ez9FApAFRsjwBmXUzFxB8niuPdlbmvIlsQhfzwPH/y8NZNmRwZXTdd9fj7cTliD0"
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)


@app.get("/")
async def root():
    return {"message": "pskovedu.ml is a top site"}


@app.post("/images/{uuid}", tags=["Images"])
async def create_upload_file(uuid: str, file: UploadFile = File(...)):
    contents = await file.read()
    with open("/home/adlem/DiaryBackend/" + uuid + ".jpg", "wb") as f:
        f.write(contents)
    return {"filename": file}


@app.get("/images/{uuid}", tags=["Images"])
async def show_image(uuid: str):
    if os.path.isfile("/home/adlem/DiaryBackend/" + uuid + ".jpg"): return FileResponse(
        "/home/adlem/DiaryBackend/" + uuid + ".jpg")
    else: return None


@app.post("/journals/diaryday", tags=["Diary day"])
async def DiaryDay(query: Q):
    r = await client.post(f"{base_url}/journals/diaryday",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM, "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()

@app.post("/journals/periodmarks", tags=["Period marks"])
async def PeriodMarks(query: Q):
    r = await client.post(f"{base_url}/journals/periodmarks",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM, "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()

@app.post("/journals/allperiods", tags=["All periods"])
async def AllPeriods(query: Q):
    r = await client.post(f"{base_url}/journals/allperiods",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM, "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/marksbyperiod", tags=["Marks by period"])
async def MarksByPeriod(query: Q):
    r = await client.post(f"{base_url}/journals/marksbyperiod",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM, "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/allmarks", tags=["All marks"])
async def AllMarks(query: Q):
    r = await client.post(f"{base_url}/journals/allmarks",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM, "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()
