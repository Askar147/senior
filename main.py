from typing import List
from fastapi import FastAPI, UploadFile, WebSocket
from tempfile import TemporaryDirectory
import tempfile
import model_call
import os

app = FastAPI()
absolute_model_path = os.path.abspath('./first_model.h5')


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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        binary_data = await websocket.receive_bytes()
        file = convert_binary_temporary(binary_data)

        with TemporaryDirectory(prefix="static-") as tmpdir:
            new_file_path = create_new_file_path(tmpdir, file.filename)
            write_file_to_directory(new_file_path, file)
            await websocket.send_text(file.filename + " : " + recognize(new_file_path))


def convert_binary_temporary(binary_data: bytes):
    file = tempfile.NamedTemporaryFile(
        max_size=1000000, mode="wb")
    file.write(binary_data)
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
