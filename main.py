import os
import random
import string
import time
import uuid
from datetime import datetime
import http3
import pymongo
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from http3 import Headers
from pydantic import BaseModel, Field
from pymongo.collection import Collection
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
import base64
from models.Q import Q
from models.TgGetCode import TgGetCode
from secret import secretize
import uvicorn
scheduler = BackgroundScheduler()
# global process variable
proc = None
client = pymongo.MongoClient("localhost", 27017)
auth_collection: Collection = client.diary.auth
pda_collection: Collection = client.diary.pda
notify_collection: Collection = client.diary.notify
tg_collection: Collection = client.diary.tg

import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("./diary-b2ba2-firebase-adminsdk-nvon7-1be3dce4d4.json")
default_app = firebase_admin.initialize_app(cred)

def XORcipher(plaintext):
    key = "ru.integrics.mobileschool"
    output = ""
    for i, character in enumerate(plaintext):
        output += chr(ord(character) ^ ord(key[i % len(key)]))
    return output
def crypt(data):
    return base64.b64encode(XORcipher(data[:len(data)//2]).encode()).decode()








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
app.add_middleware(
    CORSMiddleware,
    allow_methods=["DELETE", "GET", "POST", "PUT", "OPTIONS"],
    allow_origins=['*']
)

auths = {}


@app.get("/")
async def root():
    return {"message": "opensource top"}

@app.post("/journals/diaryday", tags=["Diary day"])
async def DiaryDay(query: Q):
    if pda_collection.find_one({"guid": query.guid}) == None: pdakey = dict(await get_pda(query.guid)).get("pdakey")
    else: pdakey = pda_collection.find_one({"guid": query.guid}).get("pdakey")
    print(pdakey)
    r = await client.post(f"{base_url}/journals/diaryday",
                          json={"apikey": crypt(query.guid), "guid": query.guid, "date": query.date,
                                "from": query.froM,
                                "to": query.to, "pdakey": pdakey},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/periodmarks", tags=["Period marks"])
async def PeriodMarks(query: Q):
    if pda_collection.find_one({"guid": query.guid}) == None: pdakey = dict(await get_pda(query.guid)).get("pdakey")
    else: pdakey = pda_collection.find_one({"guid": query.guid}).get("pdakey")
    r = await client.post(f"{base_url}/journals/periodmarks",
                          json={"apikey": crypt(query.guid), "guid": query.guid, "date": query.date,
                                "from": query.froM,
                                "to": query.to, "pdakey": pdakey},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/allperiods", tags=["All periods"])
async def AllPeriods(query: Q):
    if pda_collection.find_one({"guid": query.guid}) == None: pdakey = dict(await get_pda(query.guid)).get("pdakey")
    else: pdakey = pda_collection.find_one({"guid": query.guid}).get("pdakey")
    r = await client.post(f"{base_url}/journals/allperiods",
                          json={"apikey": crypt(query.guid), "guid": query.guid, "date": query.date,
                                "from": query.froM,
                                "to": query.to, "pdakey": pdakey},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/marksbyperiod", tags=["Marks by period"])
async def MarksByPeriod(query: Q):
    if pda_collection.find_one({"guid": query.guid}) == None: pdakey = dict(await get_pda(query.guid)).get("pdakey")
    else: pdakey = pda_collection.find_one({"guid": query.guid}).get("pdakey")
    r = await client.post(f"{base_url}/journals/marksbyperiod",
                          json={"apikey": crypt(query.guid), "guid": query.guid, "date": query.date,
                                "from": query.froM,
                                "to": query.to, "pdakey": pdakey},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()


@app.post("/journals/allmarks", tags=["All marks"])
async def AllMarks(query: Q):
    if pda_collection.find_one({"guid": query.guid}) == None: pdakey = dict(await get_pda(query.guid)).get("pdakey")
    else: pdakey = pda_collection.find_one({"guid": query.guid}).get("pdakey")
    r = await client.post(f"{base_url}/journals/allmarks",
                          json={"apikey": crypt(query.guid), "guid": query.guid, "date": query.date,
                                "from": query.froM,
                                "to": query.to, "pdakey": pdakey},
                          headers=Headers({"Content-Type": "application/json"}))
    print(r.headers)
    return r.json()

@app.post("/pda/getpdakey", tags=["PDA"])
async def get_pda(guid):
    r = await client.post(f"{base_url}/pda/getpdakey",
                          json={"apikey": "","sysguid": guid},
                          headers=Headers({"Content-Type": "application/json"}))
    if dict(r.json()).get("status") == "not found":
        raise HTTPException(404, "Вы не потвердили соглашение на обработку данных (PDA)")
    if pda_collection.find_one({"guid": guid}) is None: pda_collection.insert_one({"guid": guid, "pdakey": dict(r.json()).get("pdakey")})
    return r.json()

@app.post("/pda/setpdakey", tags=["PDA"])
async def set_pda(guid, name):
    pda_key = str(int(time.time() // 1)) + '-' + ''.join(random.choice(string.digits + string.ascii_lowercase) for i in range(8))
    r = await client.post(f"{base_url}/pda/setpdakey",
                          json={"apikey": "", "appid": "Образование Псковской области",
                                "name": name,"sysguid": guid, "pdakey": pda_key},
                          headers=Headers({"Content-Type": "application/json"}))
    if dict(r.json()).get("error") == "":
        raise HTTPException(404, "Ошибка")
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


#@app.get("/notify/register", tags=["notify"])
#async def NotifyReg(token: str):
#    if notify_collection.find_one({"token": token}) is not None: return
#    res = notify_collection.insert_one({"token": token})
#    return res.deleted_count > 0


@app.get("/notify/kr", tags=["notify"])
async def NotifyKrCreate(token: str, time: int = 18):
    #"""if notify_collection.find_one({"token": token}) is not None: raise HTTPException(400)
    #res = notify_collection.update_one({"token": token}, {"$set": {"kr": time}})
    #return "success" """
    topic = "kr_" + str(time)
    response = messaging.subscribe_to_topic(token, topic)
    if response.failure_count > 0: raise HTTPException(400, "Неверный токен")


@app.delete("/notify/kr", tags=["notify"])
async def NotifyKrDelete(token: str, time: int = 18):
    #"""if notify_collection.find_one({"token": token}) is not None: raise HTTPException(400)
    #res = notify_collection.update_one({"token": token}, {"$set": {"kr": time}})
    #return "success" """
    topic = "kr_" + str(time)
    response = messaging.unsubscribe_from_topic(token, topic)
    if response.failure_count > 0: raise HTTPException(400, "Неверный токен")



@app.get("/notify/marks", tags=["notify"])
async def NotifyMarksCreate(token: str, time: int = 18):
    #"""if notify_collection.find_one({"token": token}) is not None: raise HTTPException(400)
    #res = notify_collection.update_one({"token": token}, {"$set": {"kr": time}})
    #return "success" """
    topic = "marks_" + str(time)
    response = messaging.subscribe_to_topic(token, topic)
    if response.failure_count > 0: raise HTTPException(400, "Неверный токен")


@app.delete("/notify/marks", tags=["notify"])
async def NotifyMarksDelete(token: str, time: int = 18):
    #"""if notify_collection.find_one({"token": token}) is not None: raise HTTPException(400)
    #res = notify_collection.update_one({"token": token}, {"$set": {"kr": time}})
    #return "success" """
    topic = "marks_" + str(time)
    response = messaging.unsubscribe_from_topic(token, topic)
    if response.failure_count > 0: raise HTTPException(400, "Неверный токен")


def job(time: int, type: str):
    topic = type + "_" + str(time)
    print(topic)
    message = messaging.Message(
        data={"type": type},
        topic=topic
    )
    messaging.send(message)

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

#schedule.every(1).day.at("19:44").do(print, (18))
#schedule.every(30).seconds.do(job, (18))
job(18, "kr")
job(20, "marks")
#scheduler.add_job(job, trigger='cron', hour=18, minute=0, args=(18, "kr"))
if __name__ == '__main__':
    # create process instance and set the target to run function.
    # use daemon mode to stop the process whenever the program stopped.
    scheduler.start()
    uvicorn.run(app, host="0.0.0.0", port=8090, root_path="")
    pass
