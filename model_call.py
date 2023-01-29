import os
import librosa
import numpy as np
import tensorflow
from tensorflow import keras

inp = '/content/drive/MyDrive/Colab Notebooks/speech/audio_speech_actors_01-24/Actor_06/03-01-06-02-01-01-06.wav'
model_path = './first_model.h5'


class EmotionRecognizer():
    def __init__(self, model_path):
        self.model = keras.models.load_model(model_path)
        self.emotions = {0: 'angry', 1: 'disgust', 2: 'fear',
                         3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

    def __call__(self, inp_path):
        y, sr = librosa.load(inp_path, sr=16000)
        audio = librosa.feature.mfcc(y, sr=sr, fmin=50, n_mfcc=30)
        reformatted_audio = np.zeros((30, 150))
        for i in range(30):
            for j in range(150):
                try:
                    reformatted_audio[i][j] = audio[i][j]
                except IndexError:
                    pass
        reformatted_audio = np.array([reformatted_audio])
        result = self.model.predict(reformatted_audio)
        return self.emotions[int(np.where(result[0] == result[0].max())[0])]
