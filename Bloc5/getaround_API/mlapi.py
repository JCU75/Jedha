from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator 
import joblib
import pandas as pd
import os
from typing import List
import mlflow
import mlflow.sklearn
from pathlib import Path
from dotenv import load_dotenv


# Load .env file
file_path = Path(__file__).resolve()
parent_path = file_path.parent.parent
env_path = os.path.join(parent_path, '.env')


# Load the environment variables from the .env file if it exists
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    print("No .env file found. Using environment variables.")

# Load the environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
RUN_ID = os.getenv("RUN_ID")


# Mlflow setup
MODEL_ID = f"{RUN_ID}/model"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Load the model and preprocessor from MLflow
model = mlflow.sklearn.load_model(MODEL_ID)
artifact_path = f"{RUN_ID}/preprocessing/preprocessor.joblib"
local_path = mlflow.artifacts.download_artifacts(artifact_path)
preprocessor = joblib.load(local_path)


app = FastAPI(
    title="Car Price Prediction API",
    description="API to predict car prices rented on Getaround",
    version="1.0"
)


class CarFeatures(BaseModel):
    model_key: str = Field(..., description="Vehicle make")
    mileage: int = Field(..., description="Vehicle mileage", ge=0)
    engine_power: int = Field(..., description="Engine power in horsepower", ge=0)
    fuel: str = Field(..., description="Fuel type (diesel, petrol, hybrid_petrol, electro)")
    paint_color: str = Field(..., description="Paint color")
    car_type: str = Field(..., description="Car type (convertible, coupe, estate, hatchback, sedan, subcompact, suv, van)")
    private_parking_available: bool = Field(..., description="Private parking space available")
    has_gps: bool = Field(..., description="GPS available")
    has_air_conditioning: bool = Field(..., description="Air conditioning available")
    automatic_car: bool = Field(..., description="Car with automatic transmission")
    has_getaround_connect: bool = Field(..., description="Getaround Connect service available")
    has_speed_regulator: bool = Field(..., description="Cruise control available")
    winter_tires: bool = Field(..., description="Winter tires available")
    

# Validating value for fuel field
@validator('fuel')
def validate_fuel(cls, v):
    allowed_values = ['diesel', 'petrol', 'hybrid_petrol', 'electro']
    if v not in allowed_values:
        raise ValueError(f"'fuel' must be one of the following values : {', '.join(allowed_values)}")
    return v
    

# Validating values ​​for car type field
@validator('car_type')
def validate_car_type(cls, v):
    allowed_values = ['convertible', 'coupe', 'estate', 'hatchback', 'sedan', 'subcompact', 'suv', 'van']
    if v not in allowed_values:
        raise ValueError(f"'car_type' must be one of the following values : {', '.join(allowed_values)}")
    return v    


@app.get("/")
async def root():
    return {"message": "Predict price of a car rental"}


@app.post("/predict/")
async def predict_price(features: CarFeatures):
    """Price prediction for a car rental"""
    try:
        input_df = pd.DataFrame([{
            "model_key": features.model_key,
            "mileage": features.mileage,
            "engine_power": features.engine_power,
            "fuel": features.fuel,
            "paint_color": features.paint_color,
            "car_type": features.car_type,
            "private_parking_available": features.private_parking_available,
            "has_gps": features.has_gps,
            "has_air_conditioning": features.has_air_conditioning,
            "automatic_car": features.automatic_car,
            "has_getaround_connect": features.has_getaround_connect,
            "has_speed_regulator": features.has_speed_regulator,
            "winter_tires": features.winter_tires
        }])

        # Convert boolean columns to integers
        bool_cols = input_df.select_dtypes(include=['bool']).columns
        input_df[bool_cols] = input_df[bool_cols].astype(int)

        # Preprocess the input data
        preprocess_data = preprocessor.transform(input_df)

        # Make a prediction
        prediction = model.predict(preprocess_data)
        return {"prediction": prediction.tolist()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong in prediction: {str(e)}")
   
  
@app.post("/predicts/")
async def predict_multiple_prices(features_list: List[CarFeatures]):
    """Price predictions for multiple car rentals"""
    try:
        # Convert list of features to DataFrame
        input_data = [feature.dict() for feature in features_list]
        input_df = pd.DataFrame(input_data)

        # Convert boolean columns to integers
        bool_cols = input_df.select_dtypes(include=['bool']).columns
        input_df[bool_cols] = input_df[bool_cols].astype(int)

        # Preprocess the input data
        preprocess_data = preprocessor.transform(input_df)

        # Make predictions
        predictions = model.predict(preprocess_data)
        return {"predictions": predictions.tolist()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong in batch prediction: {str(e)}")

