const API_BASE = "http://192.168.1.11:5001";

// For phone/ngrok deployment, replace above with your backend ngrok URL:
// const API_BASE = "https://YOUR-BACKEND-NGROK-URL.ngrok-free.app";

const FALLBACK_LOCATION = {
    latitude: 16.4419,
    longitude: 80.6226
};

function sendSOS(trigger = "manual", confidence = 0) {
    const name = document.getElementById("name").value.trim();
    const status = document.getElementById("status");

    if (!name) {
        status.innerText = "Please enter your name.";
        return;
    }

    status.innerText = "Getting your live location...";

    if (!navigator.geolocation) {
        status.innerText = "GPS not supported. Sending fallback location...";
        sendToBackend(
            name,
            FALLBACK_LOCATION.latitude,
            FALLBACK_LOCATION.longitude,
            trigger,
            confidence,
            "fallback"
        );
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            status.innerText = "Live location found. Sending SOS...";

            sendToBackend(
                name,
                latitude,
                longitude,
                trigger,
                confidence,
                "live"
            );
        },

        function(error) {
            console.log("GPS Error:", error.message);

            status.innerText =
                "Live GPS unavailable. Sending fallback emergency location...";

            sendToBackend(
                name,
                FALLBACK_LOCATION.latitude,
                FALLBACK_LOCATION.longitude,
                trigger,
                confidence,
                "fallback"
            );
        },

        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }
    );
}


function sendToBackend(name, latitude, longitude, trigger, confidence, locationType) {
    const status = document.getElementById("status");

    fetch(`${API_BASE}/send-sos`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            latitude: latitude,
            longitude: longitude,
            trigger: trigger,
            confidence: confidence,
            location_type: locationType
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Backend error");
        }
        return res.json();
    })
    .then(data => {
        status.innerHTML =
            "SOS Sent Successfully!<br><br>" +
            "<a href='" + data.location + "' target='_blank'>View Location</a>";
    })
    .catch(error => {
        console.error(error);
        status.innerText = "Backend connection failed.";
    });
}


function startVoiceDetection() {
    const status = document.getElementById("status");
    const voiceText = document.getElementById("voiceText");

    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        status.innerText = "Voice detection works best in Google Chrome.";
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    status.innerText = "Listening for emergency voice command...";

    recognition.start();

    recognition.onresult = function(event) {
        const transcript =
            event.results[0][0].transcript.toLowerCase();

        voiceText.innerText = "Detected: " + transcript;

        fetch(`${API_BASE}/predict-distress`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: transcript
            })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("AI backend failed");
            }
            return res.json();
        })
        .then(data => {
            const confidence = Number(data.confidence) || 0;

            voiceText.innerText =
                "Detected: " +
                data.text +
                " | AI Confidence: " +
                confidence.toFixed(2);

            if (data.distress === true) {
                status.innerText =
                    "Distress detected. Getting live location...";

                sendSOS("voice", confidence);
            } else {
                status.innerText = "No distress detected.";
            }
        })
        .catch(error => {
            console.error(error);
            status.innerText = "AI backend error.";
        });
    };

    recognition.onerror = function(event) {
        status.innerText = "Voice error: " + event.error;
    };
}