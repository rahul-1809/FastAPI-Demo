from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated , Literal
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description = "ID of the patient", examples = ["P001", "P002"])]
    
    name: Annotated[str, Field(..., description = 'Name of the patient', examples = ['John Doe', 'Jane Smith'])]
    city : Annotated[str, Field(..., description = 'City of the patient', examples = ['New York', 'Los Angeles'])]
    height : Annotated[float, Field(..., description = 'Height of the patient in cm', examples = [170.5, 180.0])]
    weight : Annotated[float, Field(..., description = 'Weight of the patient in kg', examples = [70.5, 80.0])]
    gender : Annotated[Literal['male', 'female', 'other'], Field(..., description = "Gender of the patient")]
    age : Annotated[int, Field(..., description = 'Age of the patient in years', examples = [30, 25])] 
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / ((self.height ) ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"
    
    

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
        
    return data 

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def home():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "A fully functional API to manage your patient records."}

@app.get('/view')
def view():
    data = load_data()
    
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id : str = Path(..., description="ID of the patient in DB", example="P001")):
    data = load_data()
    
    if(patient_id in data):
        return data[patient_id]
    raise HTTPException(status_code=404, detail = 'Patient not found')

@app.get('/sort')
def sort_patients(sort_by : str = Query(..., description= "Sort on the basis of height, weight or bmi"), order : str = Query('asc', description = "Sort in asc or desc order")):
    
    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail = f"Invalid fields select from {valid_fields}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail = "Invalid order select from asc or desc")
    
    data = load_data()
    
    sort_order = True if order=='desc' else False
    
    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse=sort_order)
    
    return sorted_data

@app.post('/create')
def create_patient(patient : Patient):
    
    data = load_data()
    
    
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    # data[patient.id] = patient.dict()
    data[patient.id] = patient.model_dump(exclude = ['id'])
    
    save_data(data)
    
    return JSONResponse(status_code = 201, content={"message": "Patient created successfully", "patient_id": patient.id})
    
    
    
    
    

