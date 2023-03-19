import os
import librosa
import numpy as np
import tensorflow
from tensorflow import keras

inp = '/content/drive/MyDrive/Colab Notebooks/speech/audio_speech_actors_01-24/Actor_06/03-01-06-02-01-01-06.wav'
model_path = './first_model.h5'
absolute_model_path = os.path.abspath(model_path)


import librosa
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import OneHotEncoder

class EmotionRecognizer:
    
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.encoder = OneHotEncoder()
        self.testing = ['angry',2,'disgust',4,5,6,'sad',8]
        self.classes = ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprise']
        self.emotions = {0:'angry',1:'disgust',2:'fear',3:'happy',4:'neutral',5:'sad',6:'surprise'}

    
    def __call__(self, audio_path):
        # Load audio file and extract features
        data, sample_rate = librosa.load(audio_path, duration=2.5, offset=0.6)
        features = self.extract_features(data, sample_rate)
        # Normalize features
        features = (features - np.mean(features)) / np.std(features)
        # Reshape features for model input
        features = np.reshape(features, (1, -1))
        # Make prediction
        result = self.model.predict(features)
        # result = (x-np.min(x))/(np.max(x)-np.min(x))
        temp = []
        for i,j in zip(result[0], self.classes):
          temp.append((i,j))
        temp.sort(key = lambda x: x[0], reverse = True)
        l = {str(y):str(x) for x,y in temp}
        return l
        print(l)
        return self.classes[int(np.where(result[0] == result[0].max())[0])]

        # Decode one-hot encoded prediction
        prediction = self.encoder.inverse_transform(result)
        print(prediction)
        # Get predicted emotion label
        emotion = self.classes[int(prediction)]
        return emotion
        
    def extract_features(self, data, sample_rate):
        # ZCR
        
        result = np.array([])
        zcr = np.mean(librosa.feature.zero_crossing_rate(y=data).T, axis=0)
        result=np.hstack((result, zcr)) # stacking horizontally

        # Chroma_stft
        stft = np.abs(librosa.stft(data))
        chroma_stft = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
        result = np.hstack((result, chroma_stft)) # stacking horizontally

        # MFCC
        mfcc = np.mean(librosa.feature.mfcc(y=data, sr=sample_rate).T, axis=0)
        result = np.hstack((result, mfcc)) # stacking horizontally

        # Root Mean Square Value
        rms = np.mean(librosa.feature.rms(y=data).T, axis=0)
        result = np.hstack((result, rms)) # stacking horizontally

        # MelSpectogram
        mel = np.mean(librosa.feature.melspectrogram(y=data, sr=sample_rate).T, axis=0)
        result = np.hstack((result, mel)) # stacking horizontally
    
        return result

# balgyn was here