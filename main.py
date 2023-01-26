import difflib
import os
import base64
import os
import random
import uuid
from datetime import datetime
import http3
import pymongo
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from http3 import Headers
from jpype import JClass, JPackage
from pydantic import BaseModel, Field
from pymongo.collection import Collection
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from Crypto.Cipher import AES

from secret import secretize

client = pymongo.MongoClient("localhost", 27017)
auth_collection: Collection = client.diary.auth
tg_collection: Collection = client.diary.tg
key = "aYXfLjOMB9V5az9Ce8l+7A=="
decoded = base64.b64decode(key)
#import jpype
#import jpype.imports
#
#jpype.addClassPath("./x2dsf")
#jpype.startJVM("""-Djava.library.path=D:/Unity/DiaryBackend/""")
#testPkg = JPackage('x2')
#Test = testPkg.X()


data = "DDFED2B991D7AEE62D9A8136AD98B737"
#print(Test.m0do(str(data)))
def encrypt(text):
    # Secret key
    # Text to be encrypted
    # Initialize encryptor
    aes = AES.new(decoded, AES.MODE_ECB)
    # Aes encryption to b
    message = text.encode()
    offset = 16 - len(message) % 16
    message = message + (offset * chr(offset)).encode()
    encrypt_aes = aes.encrypt(message)
    # Converted into a string with base64
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='UTF-8')
    return encrypted_text.replace("\n", "")



class Q(BaseModel):
    guid: str = ""
    date: str = ""
    froM: str = Field(alias="from", default="")
    to: str = ""

class TgGetCode(BaseModel):
    data: str = ""


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
    allow_methods=["DELETE", "GET", "POST", "PUT", "OPTIONS"],
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
                          json={"apikey": encrypt(query.guid), "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/periodmarks", tags=["Period marks"])
async def PeriodMarks(query: Q):
    r = await client.post(f"{base_url}/journals/periodmarks",
                          json={"apikey": encrypt(query.guid), "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/allperiods", tags=["All periods"])
async def AllPeriods(query: Q):
    r = await client.post(f"{base_url}/journals/allperiods",
                          json={"apikey": encrypt(query.guid), "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/marksbyperiod", tags=["Marks by period"])
async def MarksByPeriod(query: Q):
    r = await client.post(f"{base_url}/journals/marksbyperiod",
                          json={"apikey": encrypt(query.guid), "guid": query.guid, "date": query.date, "from": query.froM,
                                "to": query.to},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/allmarks", tags=["All marks"])
async def AllMarks(query: Q):
    r = await client.post(f"{base_url}/journals/allmarks",
                          json={"apikey": encrypt(query.guid), "guid": query.guid, "date": query.date, "from": query.froM,
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

@app.post("/tg_auth/get_code", tags=["auth"])
async def GetCode(body: TgGetCode):
    code = uuid.uuid4().hex
    tg_collection.insert_one({"code": code, "data": body.data, "tg_id": 0})
    return code

@app.get("/tg_auth/login", tags=["auth"])
async def TgLogIn(code: str, tg_id: int):
    tg_collection.update_one({"code": code}, {"$set": {"tg_id": tg_id}})
    return "success"

@app.get("/tg_auth/info", tags=["auth"])
async def TgLogIn(tg_id: int, sign: str):
    user = tg_collection.find_one({"tg_id": tg_id})
    if sign != secretize(tg_id): raise HTTPException(400, "Неверная подпись")
    if user == None: raise HTTPException(404, "Не авторизован")
    return user.get("data")

