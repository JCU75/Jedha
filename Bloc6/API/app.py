import mlflow 
import uvicorn
import json
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import random
import logging
from scipy.io import wavfile
import io
import numpy as np
import librosa
from skimage.transform import resize
import os
import tensorflow as tf



librosa.cache.enable = False

logging.basicConfig(
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


description = """
API for detecting early signs of Alhzeimer's disease by voice
"""

tags_metadata = [
    {
        "name": "EchoCare",
        "description": "Endpoints that uses our Machine Learning model for detecting attrition"
    }
]

# Retrieving environment variables
MLFLOW_TRACKING_USERNAME = os.getenv("MLFLOW_TRACKING_USERNAME")
MLFLOW_TRACKING_PASSWORD = os.getenv("MLFLOW_TRACKING_PASSWORD")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")

# Configuring environment variables for MLflow
os.environ['MLFLOW_TRACKING_USERNAME'] = MLFLOW_TRACKING_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = MLFLOW_TRACKING_PASSWORD
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# logger.debug(f"MLFLOW_TRACKING_URI: {MLFLOW_TRACKING_URI}")
# logger.debug(f"Model path: {MLFLOW_TRACKING_USERNAME}")

app = FastAPI(
    title="EchoCare API",
    description=description,
    version="0.2",
    contact={
        "name": "EchoCare API - by Jedha Team FS31",
        "url": "https://jedha.co",
    },
    openapi_tags=tags_metadata

) 

#Base model
def preprocess_audio(audio_file_path): 
    """ Preprocess an audio file for the model. """ 
    target_shape = (128,128,1)
    audio_data, sample_rate = librosa.load(audio_file_path, sr=None) 
    mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
    mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max) 
    mel_spectrogram = np.expand_dims(mel_spectrogram, axis=-1) 
    mel_spectrogram = resize(mel_spectrogram, target_shape)
    # Convert the mel spectrogram to a NumPy array
    mel_spectrogram = mel_spectrogram.astype(np.float32)
    # Reshape to the expected shape (batch_size, height, width, channels)
    mel_spectrogram = np.reshape(mel_spectrogram, (1,) + target_shape) # Remove the extra dimension here
    return mel_spectrogram 


@app.post("/predict_basemodel", tags=["Base_Model"])
async def predict(file: UploadFile = File(...)):
    """
    Prediction for one observation. Endpoint will return a dictionnary like this:
    ```
    {'prediction': PREDICTION_VALUE[0,1]}
    ```
    You need to give this endpoint all columns values as dictionnary, or form data.
    """

    # Load MLflow model
    model_path = 'runs:/3ef9ca99db034304a358c0f045466344/base_model_12'
    loaded_model = mlflow.pyfunc.load_model(model_path)
    logger.debug("Model loaded successfully")
    logger.debug(f"Model path: {file}")

    # Reading the audio file in memory
    audio_data = await file.read()
    audio_file = io.BytesIO(audio_data)

    # Audio preprocessing 
    audio_features = preprocess_audio(audio_file)

    # Load model as a PyFuncModel.
    prediction = loaded_model.predict(audio_features)
    logger.debug(f"Raw prediction: {prediction}")

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response

# VGG-30
def preprocess_audio_vgg(audio_file_path):
    target_shape = (96, 1366)    
    audio_data, sample_rate = librosa.load(audio_file_path, sr=None) 
    logger.debug(f"Audio loaded - Sample rate: {sample_rate}, Shape: {audio_data.shape}")

    # Create the Mel spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
    mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

    # Resize the spectrogram to match the model's input shape
    mel_spectrogram = np.expand_dims(mel_spectrogram, axis=-1) # Expand dims for channels
    mel_spectrogram = resize(mel_spectrogram, target_shape)
    return mel_spectrogram    

@app.post("/predict_vgg", tags=["VGG_30"])
async def predict(file: UploadFile = File(...)):
    """
    Prediction for one observation. Endpoint will return a dictionnary like this:
    ```
    {'prediction': PREDICTION_VALUE[0,1]}
    ```
    You need to give this endpoint all columns values as dictionnary, or form data.
    """

    # Load MLflow model
    model_path = 'runs:/9255f4b3279e49579d3200aca4c18ba2/VGGNet_30'
    loaded_model = mlflow.pyfunc.load_model(model_path)
    logger.debug("Model loaded successfully")   
    logger.debug(f"Model path: {file}")

    # Reading the audio file in memory
    audio_data = await file.read()
    audio_file = io.BytesIO(audio_data)

    # Preprocessing the audio file
    audio_features = preprocess_audio_vgg(audio_file)

    # Load model as a PyFuncModel.
    prediction = loaded_model.predict(audio_features)
    logger.debug(f"Raw prediction: {prediction}")

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response    


@app.post("/test", tags=["Test API"])
async def predict():
    """
    Return 3 random numbers just for testing connection with API
    ```
    {'prediction': PREDICTION_VALUE[0,1]}
    ```

    You need to give this endpoint all columns values as dictionnary, or form data.
    """

    control = random.randint(1, 100) 
    mci = random.randint(1,(100-control))
    adrd = 100 - control - mci

    prediction = {
        "control": control,
        "mci": mci,
        "adrd": adrd
    }

    # Format response
    response = {"prediction": prediction}
    return response    



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)