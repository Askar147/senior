from typing import List
from fastapi import FastAPI, UploadFile, WebSocket
from fastapi.responses import HTMLResponse
from tempfile import TemporaryDirectory
import tempfile
import model_call
import os

app = FastAPI()


model_path = './first_model.h5'
absolute_model_path = os.path.abspath(model_path)

@app.post("/uploadfile/")
async def create_upload_file(file_received: List[UploadFile]):
    with TemporaryDirectory(prefix="static-") as tmpdir:
        emotions = dict()

        for file in file_received:
            new_file_path = os.path.join(tmpdir, file.filename)

            with open(new_file_path, 'wb') as file_saved:
                file_saved.write(file.file.read())

            recognizer = model_call.EmotionRecognizer(absolute_model_path)
            result = recognizer(new_file_path)

            emotions.update({file.filename: result})

        return {"results": emotions}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        binary_data = await websocket.receive_bytes()
        # Convert binary data to SpooledTemporaryFile
        file = tempfile.NamedTemporaryFile(
            max_size=1000000, mode="wb")
        file.write(binary_data)
        file.seek(0)

        with TemporaryDirectory(prefix="static-") as tmpdir:
            new_file_path = os.path.join(tmpdir, file.filename)

            with open(new_file_path, 'wb') as file_saved:
                file_saved.write(file.read())

            recognizer = model_call.EmotionRecognizer(absolute_model_path)
            result = recognizer(new_file_path)
            await websocket.send_text(f"Message text was sent: " + result)
