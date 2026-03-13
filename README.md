# DeepShield — AI Deepfake Detector
### Flask + Google Gemini Vision API (100% FREE)

---

## Project Structure

```
deepshield/
├── app.py                ← Flask server (main entry point)
├── requirements.txt      ← Python dependencies
├── README.md             ← This file
└── templates/
    └── index.html        ← Frontend UI
```

---

## ✅ Setup in 4 Steps

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Get your FREE Gemini API Key
1. Go to → https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (looks like: `AIzaSy...`)

> FREE limits: 15 requests/minute · 1,500 requests/day · No credit card needed!

### Step 3 — Set your API Key
```bash
# Linux / Mac
export GEMINI_API_KEY="AIzaSy-your-key-here"

# Windows Command Prompt
set GEMINI_API_KEY=AIzaSy-your-key-here

# Windows PowerShell
$env:GEMINI_API_KEY="AIzaSy-your-key-here"
```

### Step 4 — Run the server
```bash
python app.py
```
Open your browser → **http://localhost:5000** 🚀

---

## API Endpoints

### POST /analyze
Analyze an image for deepfake detection.

| Field  | Type   | Description                        |
|--------|--------|------------------------------------|
| image  | file   | Image file (PNG/JPG/WEBP, max 10MB)|
| source | string | Where the user got the image       |

**Response:**
```json
{
  "verdict": "DEEPFAKE",
  "confidence": 87,
  "threat_level": "HIGH",
  "authenticity_score": 13,
  "indicators": [...],
  "source_risk": "...",
  "warning": "...",
  "overview": "...",
  "facial_analysis": "...",
  "technical_analysis": "...",
  "recommendation": "...",
  "detected_manipulations": ["GAN artifacts", "Face swap"],
  "model_used": "gemini-1.5-flash",
  "analyzed_at": "2025-01-01T12:00:00Z"
}
```

### GET /health
Check server + API key status.

---

## Free Tier Limits (Gemini 1.5 Flash)
| Limit | Value |
|-------|-------|
| Requests per minute | 15 |
| Requests per day | 1,500 |
| Cost | $0.00 |
| Credit card required | No |
