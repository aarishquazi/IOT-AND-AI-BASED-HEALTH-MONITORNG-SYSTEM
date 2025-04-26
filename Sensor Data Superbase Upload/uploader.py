import serial
import time
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import threading

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# Serial Ports for Arduino
PULSE_PORT = "COM5"      # Arduino 1 (Pulse sensor)
ECG_LM35_PORT = "COM6"   # Arduino 2 (ECG + LM35)
BAUD_RATE = 9600

# Upload function
def upload_data(table, data):
    if not all(value is not None for key, value in data.items() if key not in ['device_id', 'timestamp']):
        print(f"❌ Incomplete data skipped: {data}")
        return
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}"
        response = requests.post(url, headers=HEADERS, json=data)
        if response.status_code in [200, 201]:
            print(f"✅ Uploaded to {table}: {data}")
        else:
            print(f"❌ Upload failed for {table}: {response.text}")
    except Exception as e:
        print(f"❗ Upload Exception: {e}")

# Read from Pulse Sensor
def read_pulse():
    try:
        ser = serial.Serial(PULSE_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if "Heart Rate:" in line and "BPM" in line:
                try:
                    bpm = int(line.split(":")[1].replace("BPM", "").strip())
                    if 60 <= bpm <= 120:
                        upload_data("pulse_data", {
                            "device_id": "PulseSensor_Arduino1",
                            "timestamp": datetime.utcnow().isoformat(),
                            "pulse_value": bpm
                        })
                except ValueError:
                    continue
    except Exception as e:
        print("❗ Pulse Error:", e)

# Read from ECG + LM35 Sensor
def read_ecg_lm35():
    try:
        ser = serial.Serial(ECG_LM35_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        buffer = []
        while True:
            line = ser.readline().decode(errors='ignore').strip()

            # ECG:...
            if "ecg" in line:
                try:
                    print('ecg found')
                    ecg_val = int(line.split("{")[1].split(":")[1].strip().strip('}'))
                    print(ecg_val)
                    # buffer.append(ecg_val)
                    # if len(buffer) >= 1:
                    #     avg_ecg = sum(buffer) // len(buffer)
                    #     upload_data("ecg_data", {
                    #         "device_id": "ECG_LM35_Arduino2",
                    #         "timestamp": datetime.utcnow().isoformat(),
                    #         "ecg_value": avg_ecg
                    #     })
                    #     buffer.clear()
                    upload_data("ecg_data", {
                            "device_id": "ECG_LM35_Arduino2",
                            "timestamp": datetime.utcnow().isoformat(),
                            "ecg_value": ecg_val
                        })
                except Exception:
                    print("error")

            # Temperature:...
            elif "temperature" in line:
                try:
                    temp_val = float(line.split("{")[1].split(":")[1].strip().strip('}'))
                    if 35 <= temp_val <= 37:
                        upload_data("temperature_data", {
                            "device_id": "ECG_LM35_Arduino2",
                            "timestamp": datetime.utcnow().isoformat(),
                            "temperature": temp_val
                        })
                except Exception:
                    continue

    except Exception as e:
        print("❗ ECG/LM35 Error:", e)

# Start Threads
if __name__ == "__main__":
    threading.Thread(target=read_pulse).start()
    threading.Thread(target=read_ecg_lm35).start()