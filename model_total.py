import librosa
import numpy as np
import tensorflow as tf
from keras.models import load_model


class EmotionRecognizer:
    def __init__(self, model_path):
        self.emotions = ['angry', 'surprise', 'disgust',
                         'fear', 'happy', 'neutral', 'sad']

        self.model = load_model(model_path, compile=False)
        self.sample_rate = 22050
        self.duration = 4

    def extract_features(self, data):
        result = np.array([])
        zcr = np.mean(librosa.feature.zero_crossing_rate(y=data).T, axis=0)
        result = np.hstack((result, zcr))  # stacking horizontally

        stft = np.abs(librosa.stft(data))
        chroma_stft = np.mean(librosa.feature.chroma_stft(
            S=stft, sr=self.sample_rate).T, axis=0)
        result = np.hstack((result, chroma_stft))  # stacking horizontally

        mfcc = np.mean(librosa.feature.mfcc(
            y=data, sr=self.sample_rate).T, axis=0)
        result = np.hstack((result, mfcc))  # stacking horizontally

        rms = np.mean(librosa.feature.rms(y=data).T, axis=0)
        result = np.hstack((result, rms))  # stacking horizontally

        mel = np.mean(librosa.feature.melspectrogram(
            y=data, sr=self.sample_rate).T, axis=0)
        result = np.hstack((result, mel))  # stacking horizontally
        return result

    def get_features(self, path):
        # Duration and offset are used to take care of the no audio in start and the ending of each audio files as seen above.
        data, sample_rate = librosa.load(path, duration=2.5, offset=0.6)
        res1 = self.extract_features(data)
        result = np.array(res1)
        return result

    def __call__(self, audio_path):
        mfccs = self.get_features(audio_path)
        mfccs = np.expand_dims(mfccs, axis=-1)
        predictions = self.model.predict(np.array([mfccs]))
        predictions[0] *= 100
        output = {
            'angry': str(predictions[0][0]),
            'neutral': str(predictions[0][1]+predictions[0][5]),
            'disgust': str(predictions[0][2]),
            'fear': str(predictions[0][3]),
            'happy': str(predictions[0][4]),
            'sad': str(predictions[0][6]),
            'surprise': str(predictions[0][7])
        }
        return output
