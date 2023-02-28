from typing import List
from fastapi import FastAPI, UploadFile, WebSocket, Body, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from tempfile import TemporaryDirectory
import tempfile
import model_call
import os
import base64
import ConnectionManager
import random
import string

from sqlalchemy.orm import Session

from database_pg import crud, models, schemes
from database_pg.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

absolute_model_path = os.path.abspath('./first_model.h5')
manager = ConnectionManager.ConnectionManager()


@app.get("/")
async def main():
    return {"message": "Hello world!"}


@app.post("/uploadfile/")
async def create_upload_file(file_received: List[UploadFile]):
    emotions = dict()

    with TemporaryDirectory(prefix="static-") as tmpdir:
        for file in file_received:
            new_file_path = create_new_file_path(tmpdir, file.filename)
            write_file_to_directory(new_file_path, file.file)
            emotions.update({file.filename: recognize(new_file_path)})

    return {"results": emotions}


@app.websocket("/ws/{key}/{order}")
async def websocket_endpoint(websocket: WebSocket, key: str, order: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    filename = key + "-" + str(order)
    try:
        while True:
            binary_data = await websocket.receive_text()
            file = convert_base_temporary(binary_data)

            with TemporaryDirectory(prefix="static-") as tmpdir:
                new_file_path = create_new_file_path(tmpdir, filename)
                write_file_to_directory(new_file_path, file)

                result = recognize(new_file_path)
                crud.create_result(db, key, order, result)
                await websocket.send_text(filename + " : " + result)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client disconnected")


@app.post("/testws")
async def test_websocket_endpoint(name: str, binary_data: str = Body(..., example="aGVsbG8=")):
    file = convert_base_temporary(binary_data)
    with TemporaryDirectory(prefix="static-") as tmpdir:
        new_file_path = create_new_file_path(tmpdir, name)
        write_file_to_directory(new_file_path, file)
        return name + " : " + recognize(new_file_path)


@app.get("/wsresults/{key}", response_model=list[schemes.Result])
def test_db_results(key: str, db: Session = Depends(get_db)):
    db_result = crud.get_result(db, key)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return db_result


@app.get("/token")
async def synchronous_token():
    return generate_random_string(10)


@app.post("/wsposttest/{key}/{order}")
def test_db_results_post(key: str, order: int, db: Session = Depends(get_db)):
    return crud.create_result(db, key, order, "neutralize")


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def convert_binary_temporary(binary_data: bytes):
    file = tempfile.NamedTemporaryFile(mode="wb")
    file.write(binary_data)
    file.seek(0)
    return file


def convert_base_temporary(data: str):
    decoded_data = base64.b64decode(data)
    file = tempfile.SpooledTemporaryFile(mode="wb")
    file.write(decoded_data)
    file.seek(0)
    return file


def recognize(path: str):
    recognizer = model_call.EmotionRecognizer(absolute_model_path)
    result = recognizer(path)
    return result


def create_new_file_path(dir: str, filename: str):
    new_file_path = os.path.join(dir, filename)
    return new_file_path


def write_file_to_directory(path: str, file):
    with open(path, 'wb') as file_saved:
        file_saved.write(file.read())
