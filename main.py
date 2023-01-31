from typing import List
from fastapi import FastAPI, File, UploadFile, WebSocket
from tempfile import TemporaryDirectory
import model_call as m

app = FastAPI()


@app.post("/uploadfile/")
async def create_upload_file(file_received: List[UploadFile]):
    with TemporaryDirectory(prefix="static-") as tmpdir:
        dict_emotions = dict()

        for file in file_received:
            new_file_path = tmpdir + "/" + file.filename

            with open(new_file_path, 'wb') as file_saved:
                file_saved.write(file.file.read())

            recognizer = m.EmotionRecognizer('.\\first_model.h5')
            result = recognizer(new_file_path)

            dict_emotions.update({file.filename: result})

        return {"results": dict_emotions}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        with open("audio.wav", "wb") as f:
            f.write(data)
            await websocket.send_text(f"Message was: {f.read()}")
        await websocket.send_text(f"Message text was sent")
