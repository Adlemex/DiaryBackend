import os

from fastapi import FastAPI, UploadFile, File
from fastapi.openapi.models import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/images/{uuid}")
async def create_upload_file(uuid: str, file: UploadFile = File(...)):

    contents = await file.read()
    with open(uuid + ".jpg", "wb") as f:
        f.write(contents)
    return {"filename": file}

@app.get("/images/{uuid}")
async def show_image(uuid: str):
    if os.path.isfile(uuid + ".jpg"): return FileResponse(uuid + ".jpg")
    else: return FileResponse("user.png")

