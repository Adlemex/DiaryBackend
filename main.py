import os
import random
from random import Random
from datetime import datetime
import pymongo
import http3
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.openapi.models import Response
from http3 import Headers
from pymongo.collection import Collection
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from pydantic import BaseModel, Field

client = pymongo.MongoClient("localhost", 27017)
auth_collection: Collection = client.diary.auth


class Q(BaseModel):
    guid: str = ""
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
    {
        "name": "Auth",
        "description": "Авторизация в веб-версии",
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

auths = {}


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
    if os.path.isfile("/home/adlem/DiaryBackend/" + uuid + ".jpg"):
        return FileResponse(
            "/home/adlem/DiaryBackend/" + uuid + ".jpg")
    else:
        return None


@app.post("/journals/diaryday", tags=["Diary day"])
async def DiaryDay(query: Q):
    r = await client.post(f"{base_url}/journals/diaryday",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/periodmarks", tags=["Period marks"])
async def PeriodMarks(query: Q):
    r = await client.post(f"{base_url}/journals/periodmarks",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/allperiods", tags=["All periods"])
async def AllPeriods(query: Q):
    r = await client.post(f"{base_url}/journals/allperiods",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/marksbyperiod", tags=["Marks by period"])
async def MarksByPeriod(query: Q):
    r = await client.post(f"{base_url}/journals/marksbyperiod",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/allmarks", tags=["All marks"])
async def AllMarks(query: Q):
    r = await client.post(f"{base_url}/journals/allmarks",
                          json={"apikey": apikey, "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.get("/auth/get_key", tags=["auth"])
async def GetKey(request: Request):
    key = random.randint(100000000, 999999999)
    auth_collection.insert_one({"key": key, "device": request.headers.get("User-Agent"), "date": datetime.now()})
    return key


@app.post("/auth/do_auth", tags=["auth"])
async def DoAuth(code: int, guid: str, messages_guid: str, name: str):
    if auth_collection.find_one({"key": code}) is not None:
        if auth_collection.find_one({"key": code}).get("guid") is not None: return False
        auth_collection.update_one({"key": code},
                                   {"$set": {"guid": guid, "messages_guid": messages_guid, 'name': name}})
        return True
    return False


@app.get("/auth/verify", tags=["auth"])
async def Verify(code: int):
    user = auth_collection.find_one({"key": code})
    if (user is None) or (user.get("guid") is None): return {}
    user = dict(user)
    user.pop("_id")
    return user

@app.get("/auth/login", tags=["auth"])
async def LogIn(code: int):
    user = auth_collection.find_one({"key": code})
    if (user is None) or (user.get("guid") is None): return {}
    user = dict(user)
    user.pop("_id")
    auth_collection.update_one({"key": code},
                               {"$set": {"last_login": datetime.now()}})
    return user

@app.delete("/auth/logout", tags=["auth"])
async def LogOut(code: int):
    res = auth_collection.delete_one({"key": code})
    return res.deleted_count > 0


@app.get("/auth/sessions", tags=["auth"])
async def SessionsList(guid: str):
    users = auth_collection.find({"guid": guid})
    res = []
    for user in users:
        user = dict(user)
        user.pop("_id")
        res.append(user)
    return res
