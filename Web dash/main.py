from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import requests
import numpy as np
import tensorflow as tf
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
import cv2
import numpy as np
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# Directories
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# FastAPI Setup
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Load the model
model = tf.keras.models.load_model("model.h5")

# Initialize LangChain Groq
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    groq_api_key=GROQ_API_KEY
)

# Create health analysis prompt template
HEALTH_ANALYSIS_TEMPLATE = (
    "You are a medical AI assistant providing health analysis reports.\n"
    "Analyze the following health vitals and provide a comprehensive health report:\n\n"
    "Vital Signs:\n"
    "- Body Temperature: {temperature}°C\n"
    "- Pulse Rate: {pulse_rate} BPM\n"
    "- ECG Analysis: {ecg_result} (Confidence: {ecg_confidence:.2f})\n\n"
    "Patient Information: \n"
    "- Patient Name: {name}\n"
    "- Date of Report: {date}°C\n"
    "Please provide a detailed analysis including:\n"
    "1. Overall health assessment\n"
    "2. Analysis of each vital sign\n"
    "3. Potential concerns or recommendations\n"
    "4. General health advice\n\n"
    "Format the response in a clear, professional manner suitable for a medical report.\n"
    "Use bullet points and sections for better readability."
)

health_prompt = ChatPromptTemplate.from_template(HEALTH_ANALYSIS_TEMPLATE)

# Utility function to fetch Supabase data
def fetch_data(table: str, limit: int = 100):
    url = f"{SUPABASE_URL}/rest/v1/{table}?order=timestamp.desc&limit={limit}"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else []

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("live-vitals.html", {"request": request})

@app.get("/real-time-ecg", response_class=HTMLResponse)
async def ecg_graph(request: Request):
    return templates.TemplateResponse("real-timeecg.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse("patient-history.html", {"request": request})

@app.get("/ai-prediction", response_class=HTMLResponse)
async def ai_prediction(request: Request):
    return templates.TemplateResponse("AI-ecg-prediction.html", {"request": request})

@app.get("/report-generator", response_class=HTMLResponse)
async def report_generator(request: Request):
    return templates.TemplateResponse("report-generator.html", {"request": request})

@app.get("/live-data")
async def live_data():
    ecg = fetch_data("ecg_data", 1)
    temp = fetch_data("temperature_data", 1)
    pulse = fetch_data("pulse_data", 1)
    return {
        "ecg_value": ecg[0]["ecg_value"] if ecg else None,
        "temperature": temp[0]["temperature"] if temp else None,
        "pulse_value": pulse[0]["pulse_value"] if pulse else None,
        "timestamp": ecg[0].get("timestamp") if ecg else None,
        "device_id": ecg[0].get("device_id") if ecg else None
    }

@app.get('/about', response_class=HTMLResponse)
def about(request:Request):
    return templates.TemplateResponse('about.html',{'request': request})

@app.get("/all-data")
async def all_data():
    ecg = fetch_data("ecg_data")
    temp = fetch_data("temperature_data")
    pulse = fetch_data("pulse_data")
    merged = ecg + temp + pulse
    merged.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return merged

@app.get("/recent-ecg")
async def recent_ecg():
    ecg = fetch_data("ecg_data", 30)
    return list(reversed(ecg))

@app.post("/predict-ecg-image")
async def predict_ecg_image(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (224, 224))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)
    result = "Abnormal" if prediction[0][0] < 0.5 else "Normal"
    return {"result": result, "probability": float(prediction[0][0])}

@app.post("/upload-snapshot-to-supabase")
async def upload_snapshot(file: UploadFile = File(...), label: str = Form(...)):
    # Read file contents
    filename = file.filename
    content = await file.read()
    
    # Setup headers for Supabase upload
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": file.content_type
    }
    
    # Upload to Supabase Storage (bucket: ecg-images)
    res = requests.put(
        f"{SUPABASE_URL}/storage/v1/object/ecg-images/{filename}",
        headers=headers,
        data=content
    )
    
    # Check if the upload was successful
    if res.status_code in [200, 201]:
        return {"message": "Snapshot uploaded successfully!"}
    return JSONResponse(content={"error": res.text}, status_code=res.status_code)

@app.post("/generate-report")
async def generate_report(
    name: str = Form(...),
    temperature: float = Form(...),
    pulseRate: int = Form(...),
    ecgImage: UploadFile = File(...)
):
    try:
        # Read and preprocess ECG image
        contents = await ecgImage.read()
        npimg = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (224, 224))
        img = img.astype("float32") / 255.0
        img = np.expand_dims(img, axis=0)

        # Predict using model
        prediction = model.predict(img)
        ecg_result = "Abnormal" if prediction[0][0] < 0.5 else "Normal"
        ecg_confidence = float(prediction[0][0])
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist)
        # Generate report with LLM (LangChain or similar)
        messages = health_prompt.format_messages(
            temperature=temperature,
            pulse_rate=pulseRate,
            ecg_result=ecg_result,
            ecg_confidence=ecg_confidence,
            name=name,
            date=now_ist.strftime("%d-%m-%Y %I:%M:%S %p")
        )
        response = llm.invoke(messages)
        report = response.content

        return {
            "report": report,
            "name": name,
            "timestamp": now_ist.strftime("%d-%m-%Y %I:%M:%S %p"),
            "vitals": {
                "temperature": temperature,
                "pulse_rate": pulseRate,
                "ecg_result": ecg_result,
                "ecg_confidence": ecg_confidence
            }
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generating report: {str(e)}"}
        )
