
from fastapi import FastAPI, File, UploadFile
from roboflow import Roboflow
import cv2
import numpy as np
import pickle
import os

app = FastAPI()


# Initialize Roboflow
rf = Roboflow(api_key="crcxvzrMUhqJYcyMcpW8")
project = rf.workspace("drone-parking-management-system").project("drone-parking-detection")
model = project.version(3).model

# Load Parking Data
PARKING_DATA_PATH = "parking_data.pkl"
if os.path.exists(PARKING_DATA_PATH):
    with open(PARKING_DATA_PATH, 'rb') as f:
        parking_data = pickle.load(f)
else:
    print("Warning: parking_data.pkl not found! API will fail on requests.")
    parking_data = []

@app.post("/detect")
async def detect_parking(file: UploadFile = File(...)):
    #  Handle Input (Receive image from request) 
    contents = await file.read()
    nparr = np.fromstring(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    temp_filename = "temp_upload.jpg"
    cv2.imwrite(temp_filename, image)

    #  Run Inference 
    # confidence=50 (0.50), overlap=30
    response = model.predict(temp_filename, confidence=50, overlap=30).json()
    predictions = response['predictions']

    # Convert predictions
    boxes = []
    for pred in predictions:
        x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
        x1, x2 = int(x - w / 2), int(x + w / 2)
        y1, y2 = int(y - h / 2), int(y + h / 2)
        
        # Filter logic
        cx, cy = int(x), int(y)
        is_valid = False
        for spot in parking_data:
            polygon = np.array(spot[0], np.int32)
            if cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0:
                is_valid = True
                break
        
        if is_valid:
            boxes.append([x1, y1, x2, y2])

    # Occupancy Logic 
    occupied_spots = []
    free_spots = []

    for spot in parking_data:
        polygon_points = np.array(spot[0], np.int32)
        spot_id = spot[1]
        is_occupied = False

        for box in boxes:
            x1, y1, x2, y2 = box
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            if cv2.pointPolygonTest(polygon_points, (cx, cy), False) >= 0:
                is_occupied = True
                break

        if is_occupied:
            occupied_spots.append(spot_id)
        else:
            free_spots.append(spot_id)

    # Return JSON Response 
    return {
        "total_detected": len(boxes),
        "occupied_count": len(occupied_spots),
        "free_count": len(free_spots),
        "occupied_spots": occupied_spots,
        "free_spots": free_spots
    }

# To run this: uvicorn main:app --reload