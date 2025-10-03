import gradio as gr
import requests
import pandas as pd
import json
import os

# API url
API_BASE_URL = "https://ungjeanclaude-api-get-around.hf.space"
PREDICT_SINGLE_URL = f"{API_BASE_URL}/predict/" 
PREDICT_MULTIPLE_URL = f"{API_BASE_URL}/predicts/"

def predict_single(model_key, mileage, engine_power, fuel, paint_color, car_type,
                  private_parking_available, has_gps, has_air_conditioning,
                  automatic_car, has_getaround_connect, has_speed_regulator, winter_tires):

    payload = {
        "model_key": model_key,
        "mileage": mileage,
        "engine_power": engine_power,
        "fuel": fuel,
        "paint_color": paint_color,
        "car_type": car_type,
        "private_parking_available": private_parking_available,
        "has_gps": has_gps,
        "has_air_conditioning": has_air_conditioning,
        "automatic_car": automatic_car,
        "has_getaround_connect": has_getaround_connect,
        "has_speed_regulator": has_speed_regulator,
        "winter_tires": winter_tires
    }

    try:
        response = requests.post(PREDICT_SINGLE_URL, json=payload)
        if response.status_code == 200:
            prediction_list = response.json()["prediction"]
            prediction = prediction_list[0]
            return f"Estimated price : {prediction:.2f}$"
        else:
            return f"Erreur API : {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error while calling : {e}"

def predict_multiple(vehicles_list):
    if not vehicles_list:
        return "Please add at least one vehicle to the list before predicting prices"
    
    try:
        # Convert vehicle list to JSON payload
        payload = vehicles_list
        
        # API call for multiple predictions
        response = requests.post(PREDICT_MULTIPLE_URL, json=payload)
        
        if response.status_code == 200:
            predictions = response.json()["predictions"]
            
            # Creating a DataFrame for the results
            df = pd.DataFrame(vehicles_list)
            df['predicted_price'] = predictions
            
            # Save results to a CSV file
            tmp_dir = "/tmp"
            os.makedirs(tmp_dir, exist_ok=True)
            result_path = os.path.abspath(os.path.join(tmp_dir, "predictions_results.csv"))
            df.to_csv(result_path, index=False)
            print("CSV created at:", result_path)
            
            # Create a text representation of the results
            results_text = f"Predictions made for {len(predictions)} vehicles:\n\n"
            
            for i in range(len(vehicles_list)):
                results_text += f"Vehicles {i+1}: {vehicles_list[i]['model_key']} - Predicted price: {predictions[i]:.2f}$\n"
           
            return results_text, result_path
        else:
            return f"ERROR API : {response.status_code} - {response.text}", None
    except Exception as e:
        return f"Error sending data : {str(e)}"

def add_vehicle_to_list(vehicles_list, model_key, mileage, engine_power, fuel, paint_color, car_type,
                        private_parking_available, has_gps, has_air_conditioning,
                        automatic_car, has_getaround_connect, has_speed_regulator, winter_tires):
    
    # Create a dictionary for the new vehicle
    new_vehicle = {
        "model_key": model_key,
        "mileage": mileage,
        "engine_power": engine_power,
        "fuel": fuel,
        "paint_color": paint_color,
        "car_type": car_type,
        "private_parking_available": private_parking_available,
        "has_gps": has_gps,
        "has_air_conditioning": has_air_conditioning,
        "automatic_car": automatic_car,
        "has_getaround_connect": has_getaround_connect,
        "has_speed_regulator": has_speed_regulator,
        "winter_tires": winter_tires
    }
    
    # Add the vehicle to the existing list (or create a new list)
    vehicles = vehicles_list.copy() if vehicles_list else []
    vehicles.append(new_vehicle)
    
    # Create a text summary of the current vehicle list
    summary = f"List of vehicles ({len(vehicles)}):\n"
    for i, vehicle in enumerate(vehicles):
        summary += f"{i+1}. {vehicle['model_key']} - {vehicle['car_type']} - {vehicle['mileage']} km\n"
    
    # Reset form fields for the next vehicle
    # (Default values ​​are set for fields in the interface))
    
    return vehicles, summary, "", 0, 0, "diesel", "", "sedan", False, False, False, False, False, False, False

def predict_multiple_csv(csv_file):
    if csv_file is None:
        return "Please upload a CSV file."
    
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file.name)
        
        # Convert the DataFrame to a list of dictionaries
        payload = df.to_dict(orient='records')
        
        # API call to predict multiple prices
        response = requests.post(PREDICT_MULTIPLE_URL, json=payload)
        
        if response.status_code == 200:
            predictions = response.json()["predictions"]
            
            # Add the predictions to the DataFrame
            df['predicted_price'] = predictions
            
            # Create a file path for the results
            result_path = "predictions_results.csv"
            df.to_csv(result_path, index=False)
            
            # Create a text string with the results
            results_text = f"Prediction made for {len(predictions)} cars.\n\n"
            results_text += "Overview of the first 5 predictions:\n"
            
            for i, (_, row) in enumerate(df.head(5).iterrows()):
                results_text += f"Vehicle {i+1}: {row['model_key']} - Predicted price: {row['predicted_price']:.2f}€\n"
            
            results_text += f"\nThe complete results were recorded in {result_path}"
            
            return results_text
        else:
            return f"ERROR API : {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error parsing or sending data : {str(e)}"

def reset_inputs():
    return (
        "",     # model_key
        0,      # mileage
        0,      # engine_power
        None,   # fuel
        "",     # paint_color
        None,   # car_type
        False,  # private_parking_available
        False,  # has_gps
        False,  # has_air_conditioning
        False,  # automatic_car
        False,  # has_getaround_connect
        False,  # has_speed_regulator
        False   # winter_tires
    )    

# Single prediction tab
with gr.Blocks(title="Single price prediction") as single_prediction_tab:
    gr.Markdown("## Single price estimate", height=50)
    gr.Markdown("Fill in a vehicle's information to estimate its rental price")
    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=100):
            model_key = gr.Textbox(label="Model key")
            mileage = gr.Number(label="Mileage")
            engine_power = gr.Number(label="Engine power")

        with gr.Column(scale=1, min_width=100):
            fuel = gr.Dropdown(["diesel", "petrol", "hybrid_petrol", "electro"], label="Fuel type")
            paint_color = gr.Textbox(label="Paint color")
            car_type = gr.Dropdown(["convertible", "coupe", "estate", "hatchback", "sedan", "subcompact", "suv", "van"], label="Car type")
            
        with gr.Column(scale=1, min_width=100):
            private_parking_available = gr.Checkbox(label="🅿️ Private parking available")
            has_gps = gr.Checkbox(label="🛰️ Gps")
            has_air_conditioning = gr.Checkbox(label="❄️ Air conditioning")
            automatic_car = gr.Checkbox(label="🎚️ Automatic gear")
            
        with gr.Column(scale=1, min_width=100):
            has_getaround_connect = gr.Checkbox(label="📱 Getaround Connect")
            has_speed_regulator = gr.Checkbox(label="💯 Speed regulator")
            winter_tires = gr.Checkbox(label="🛞 Winter tires")

    with gr.Row():
        reset_btn = gr.Button("Reset")
        predict_btn = gr.Button("Submit", variant="primary")
        download_btn = gr.DownloadButton("Download results", label="Download results", visible=False)


    predict_btn.click(
        predict_single, 
        inputs=[
            model_key, mileage, engine_power, fuel, paint_color, car_type,
            private_parking_available, has_gps, has_air_conditioning, automatic_car,
            has_getaround_connect, has_speed_regulator, winter_tires], 
        outputs=gr.Textbox(label="Result", lines=5, interactive=False))
    
    reset_btn.click(
        reset_inputs,
        inputs=[],
        outputs=[
            model_key, mileage, engine_power, fuel, paint_color, car_type,
            private_parking_available, has_gps, has_air_conditioning,
            automatic_car, has_getaround_connect, has_speed_regulator, winter_tires
        ])

# Multi-vehicle tab to add multiple vehicles manually
with gr.Blocks(title="Multiple Prediction") as multiple_prediction_tab:
    gr.Markdown("## Multiple price estimate", height=50)
    gr.Markdown("Fill in the information for each vehicle and add it to the list")
    
    # State variable to store the list of vehicles
    vehicles_list_state = gr.State([])
    
    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=100):
            model_key = gr.Textbox(label="Model key")
            mileage = gr.Number(label="Mileage")
            engine_power = gr.Number(label="Engine power")

        with gr.Column(scale=1, min_width=100):
            fuel = gr.Dropdown(["diesel", "petrol", "hybrid_petrol", "electro"], label="Fuel type")
            paint_color = gr.Textbox(label="Paint color")
            car_type = gr.Dropdown(["convertible", "coupe", "estate", "hatchback", "sedan", "subcompact", "suv", "van"], label="Car type")
            
        with gr.Column(scale=1, min_width=100):
            private_parking_available = gr.Checkbox(label="🅿️ Private parking available")
            has_gps = gr.Checkbox(label="🛰️ Gps")
            has_air_conditioning = gr.Checkbox(label="❄️ Air conditioning")
            automatic_car = gr.Checkbox(label="🎚️ Automatic gear")
            
        with gr.Column(scale=1, min_width=100):
            has_getaround_connect = gr.Checkbox(label="📱 Getaround Connect")
            has_speed_regulator = gr.Checkbox(label="💯 Speed regulator")
            winter_tires = gr.Checkbox(label="🛞 Winter tires")
    
    # Row with buttons
    with gr.Row():
        add_btn = gr.Button("Add Car")
        predicts_btn = gr.Button("Submit", variant="primary")

    # Row with outputs
    with gr.Row():
        vehicles_summary = gr.Textbox(label="List of vehicles", lines=5, interactive=False)
        results_output = gr.Textbox(label="Results", lines=5, interactive=False)

    # Row with download button
    with gr.Row():
        download_btn = gr.DownloadButton(label="Download predictions CSV", interactive=True)    
    
    # Link the add button to the function to add a vehicle to the list
    add_btn.click(
        fn=add_vehicle_to_list,
        inputs=[
            vehicles_list_state,
            model_key, mileage, engine_power, fuel, paint_color, car_type,
            private_parking_available, has_gps, has_air_conditioning,
            automatic_car, has_getaround_connect, has_speed_regulator, winter_tires
        ],
        outputs=[
            vehicles_list_state, vehicles_summary,
            model_key, mileage, engine_power, fuel, paint_color, car_type,
            private_parking_available, has_gps, has_air_conditioning,
            automatic_car, has_getaround_connect, has_speed_regulator, winter_tires
        ]
    )
    
    # Link the predict button to the function to predict prices for all vehicles in the list
    predicts_btn.click(
        fn=predict_multiple,
        inputs=[vehicles_list_state],
        outputs=[results_output, download_btn]
    )

# Multi-vehicle tab with CSV file
csv_tab = gr.Interface(
    fn=predict_multiple_csv,
    inputs=gr.File(label="CSV file containing the vehicles"),
    outputs="text",
    title="Estimate via CSV file",
    description="Upload a CSV file containing data from multiple vehicles to estimate their prices."
)

# Tabbed interface
demo = gr.TabbedInterface(
    [single_prediction_tab, multiple_prediction_tab, csv_tab],
    ["Single Prediction", "Multiple Prediction", "Multiple Prediction with CSV file"],
    title="Project GetAround - Rent Price Prediction",
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    demo.launch()