from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

TOKEN = os.getenv("8739495996:AAHoy0mhH0wn7IrX4xrhkMAEcjmJ7mg_lLM")
CHAT_ID = os.getenv("2145164077")

def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram token or chat ID missing")
        return {"ok": False}

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

    print("Telegram Response:", response.json())
    return response.json()

def detect_distress(text):
    text = text.lower()

    distress_words = [
        "help",
        "help me",
        "please help",
        "save me",
        "danger",
        "emergency",
        "attack",
        "someone is following me",
        "follow me",
        "i am scared"
    ]

    distress = any(word in text for word in distress_words)
    confidence = 0.95 if distress else 0.10

    return distress, confidence

@app.route("/")
def home():
    return "HerShield Backend Running"

@app.route("/predict-distress", methods=["POST"])
def predict_distress_route():
    data = request.get_json()
    text = data.get("text", "")

    distress, confidence = detect_distress(text)

    return jsonify({
        "text": text,
        "distress": distress,
        "confidence": confidence,
        "confidence_percent": round(confidence * 100, 2)
    })

@app.route("/send-sos", methods=["POST"])
def send_sos():
    data = request.get_json()

    name = data.get("name", "Unknown User")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    trigger = data.get("trigger", "manual")
    confidence = float(data.get("confidence", 0))
    location_type = data.get("location_type", "live")

    location_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    telegram_message = f"""
🚨 EMERGENCY ALERT 🚨

User: {name}
Trigger: {trigger}
Location Type: {location_type}
AI Confidence: {round(confidence * 100, 2)}%

Time: {current_time}

Live Location:
{location_link}
"""

    send_telegram(telegram_message)

    return jsonify({
        "success": True,
        "message": "SOS sent successfully",
        "location": location_link
    })

@app.route("/history", methods=["GET"])
def history():
    return jsonify([])

if __name__ == "__main__":
    app.run()