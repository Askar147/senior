from typing import List
from fastapi import FastAPI, UploadFile, WebSocket, Body, WebSocketDisconnect, HTTPException, Depends, File
from fastapi.middleware.cors import CORSMiddleware
from tempfile import TemporaryDirectory
import tempfile
import model_call
import os
import base64
import ConnectionManager
import random
import string
import io

from sqlalchemy.orm import Session

from database_pg import crud, models, schemes
from database_pg.database import SessionLocal, engine

from pydub import AudioSegment

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


@app.get("/api/")
async def main():
    return {"message": "Hello world!"}


@app.post("/api/uploadsinglefile")
async def create_upload_single_file(file_received: UploadFile = File(description="Single files as UploadFile")):
    emotions = dict()
    segment_length_ms = 3000
    with TemporaryDirectory(prefix="static-") as tmpdir:
        mp3_audio = AudioSegment.from_file(io.BytesIO(await file_received.read()), format="mp3")

        for i, segment in enumerate(mp3_audio[::segment_length_ms]):
            filename = f"segment_{i}.wav"
            output_file = create_new_file_path(tmpdir, filename)
            segment.export(output_file, format="wav")
            emotions.update({filename: recognize(output_file)})

        return {"results": emotions}


@app.post("/api/uploadfiles/")
async def create_upload_files(file_received: List[UploadFile] = File(description="Multiple files as UploadFile")):
    emotions = dict()

    with TemporaryDirectory(prefix="static-") as tmpdir:
        for file in file_received:
            mp3_audio = AudioSegment.from_file(io.BytesIO(await file.read()), format="mp3")
            wav_audio = mp3_audio.export(format="wav")

            new_file_path = create_new_file_path(tmpdir, "converted_audio.wav")
            write_file_to_directory(new_file_path, wav_audio)
            emotions.update({file.filename: recognize(new_file_path)})

    return {"results": emotions}


@app.post("/api/uploadfile/")
async def create_upload_file(file_received: UploadFile = File(description="Single files as UploadFile")):

    with TemporaryDirectory(prefix="static-") as tmpdir:
        mp3_audio = AudioSegment.from_file(io.BytesIO(await file_received.read()), format="mp3")
        wav_audio = mp3_audio.export(format="wav")

        new_file_path = create_new_file_path(tmpdir, "converted_audio.wav")
        write_file_to_directory(new_file_path, wav_audio)

        return {file_received.filename: recognize(new_file_path)}


@app.websocket("/ws/{key}")
async def websocket_endpoint(websocket: WebSocket, key: str, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    order = 0
    try:
        while True:
            binary_data = await websocket.receive_text()
            order += 1
            filename = key + "-" + str(order)

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


@app.post("/api/testws")
async def test_websocket_endpoint(name: str, binary_data: str = Body(..., example="aGVsbG8=")):
    file = convert_base_temporary(binary_data)
    with TemporaryDirectory(prefix="static-") as tmpdir:
        new_file_path = create_new_file_path(tmpdir, name)
        write_file_to_directory(new_file_path, file)
        return name + " : " + recognize(new_file_path)


@app.get("/api/wsresults/{key}", response_model=list[schemes.Result])
def test_db_results(key: str, db: Session = Depends(get_db)):
    db_result = crud.get_result(db, key)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return db_result


@app.get("/api/token")
async def synchronous_token():
    return generate_random_string(10)


@app.post("/api/wsposttest/{key}/{order}")
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
