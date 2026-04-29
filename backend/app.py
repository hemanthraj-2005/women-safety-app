from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import pickle

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except:
    FIREBASE_AVAILABLE = False

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False


app = Flask(__name__)
CORS(app)

TOKEN = "8739495996:AAHoy0mhH0wn7IrX4xrhkMAEcjmJ7mg_lLM"
CHAT_ID = "2145164077"

db = None

if FIREBASE_AVAILABLE:
    try:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase connected.")
    except Exception as e:
        print("Firebase not connected:", e)

model = None
tokenizer = None

if ML_AVAILABLE:
    try:
        model = load_model("distress_model.h5")
        with open("tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        print("TensorFlow model loaded.")
    except Exception as e:
        print("ML model not loaded:", e)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

    print("Telegram Response:", response.json())
    return response.json()


@app.route("/predict-distress", methods=["POST"])
def predict_distress():
    data = request.get_json()
    text = data.get("text", "").lower()

    distress_words = [
        "help",
        "help me",
        "please help",
        "save me",
        "danger",
        "emergency",
        "attack",
        "someone is following me"
    ]

    distress = any(word in text for word in distress_words)

    return jsonify({
        "text": text,
        "distress": distress,
        "confidence": 0.95 if distress else 0.10
    })

@app.route("/")
def home():
    return "HerShield Backend Running"


@app.route("/predict-distress", methods=["POST"])
def predict_distress():
    data = request.get_json()
    text = data.get("text", "")

    distress, confidence = predict_distress_text(text)

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

    alert_data = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "trigger": trigger,
        "location_type": location_type,
        "confidence": confidence,
        "confidence_percent": round(confidence * 100, 2),
        "location": location_link,
        "time": current_time
    }

    if db:
        try:
            db.collection("alerts").add(alert_data)
        except Exception as e:
            print("Firestore save failed:", e)

    return jsonify({
        "success": True,
        "message": "SOS sent successfully",
        "location": location_link,
        "alert": alert_data
    })


@app.route("/history", methods=["GET"])
def history():
    if not db:
        return jsonify([])

    alerts = []

    try:
        docs = db.collection("alerts").stream()
        for doc in docs:
            item = doc.to_dict()
            item["id"] = doc.id
            alerts.append(item)
    except Exception as e:
        print("History fetch failed:", e)

    alerts.reverse()
    return jsonify(alerts)


if __name__ == "__main__":
    app.run()