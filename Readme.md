# 🚀 TruFindAI Backend

AI-powered website analysis and sales automation platform with Sara AI agent.

## 📋 Features

- ✅ Automatic website analysis (AI Visibility + SEO)
- ✅ ChatGPT-powered scoring system
- ✅ Sara AI sales agent (Twilio + OpenAI)
- ✅ Call recording & transcription
- ✅ Lead management dashboard
- ✅ Real-time analysis history

## 🛠️ Tech Stack

- **Backend:** FastAPI + Python 3.11
- **Database:** MongoDB
- **AI:** OpenAI GPT-4 + Whisper + TTS
- **Telephony:** Twilio
- **Storage:** AWS S3
- **APIs:** PageSpeed Insights, ChatGPT

## 📦 Installation

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/trufindai-backend.git
cd trufindai-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

5. **Run the server**
```bash
uvicorn main:app --reload
```

Server will start at: `http://localhost:8000`

---

### Docker Development

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Stop containers**
```bash
docker-compose down
```

3. **View logs**
```bash
docker-compose logs -f backend
```

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:
```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=

# OpenAI
OPENAI_API_KEY=your_openai_key

# PageSpeed
PAGESPEED_API_KEY=

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=trufindai-recordings
```

---

## 📡 API Endpoints

### Analysis
- `POST /api/v1/analyze` - Analyze a website
- `GET /api/v1/history` - Get analysis history

### Sara Agent
- `POST /api/v1/sara/call` - Trigger Sara call
- `GET /api/v1/sara/status/{call_id}` - Get call status

### Webhooks
- `POST /api/v1/webhooks/twilio` - Twilio callback handler

### Recordings
- `GET /api/v1/recordings/{call_id}` - Get call recording
- `GET /api/v1/transcripts/{call_id}` - Get call transcript

---

## 🧪 Testing
```bash
# Run tests (when added)
pytest

# Check code coverage
pytest --cov=app
```

---

## 📚 Documentation

Once running, visit:
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🚀 Deployment

### Deploy to Render/Railway/Heroku

1. Push to GitHub
2. Connect your repo to hosting platform
3. Add environment variables
4. Deploy!

### Deploy to VPS (DigitalOean/AWS/Linode)
```bash
# On your server
git clone your-repo
cd trufindai-backend
docker-compose up -d
```

---

## 📝 Project Structure
```
trufindai-backend/
│
├── main.py                    # 🚀 Main FastAPI app
│
├── app/
│   ├── __init__.py           
│   ├── config.py              # All configs (MongoDB, Twilio, OpenAI, etc.)
│   │
│   ├── models.py              # All MongoDB models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analysis.py        # POST /analyze
│   │   ├── sara.py            # POST /sara/call
│   │   ├── history.py         # GET /history
│   │   ├── recordings.py      # ✅ GET /recordings/{call_id}
│   │   └── webhooks.py        # POST /twilio/webhook
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper.py         # Website scraping
│   │   ├── scoring.py         # ChatGPT + PageSpeed scoring
│   │   ├── sara_agent.py      # Sara AI conversation
│   │   ├── twilio_service.py  # Twilio calls
│   │   ├── openai_service.py  # ✅ OpenAI (GPT-4, Whisper, TTS)
│   │   └── storage_service.py # ✅ AWS S3 storage
│   │
│   └── utils.py               # Helper functions
│
├── .env                       
├── .env.example               
├── .gitignore                 
├── requirements.txt           
├── Dockerfile                 
├── docker-compose.yml         
└── README.md
```
---
## How to Run

uvicorn main:app --reload
---


---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License - see LICENSE file

---

## 💬 Support

For issues or questions:
- Email: semonshaikat702@gmail.com
---

Made with ❤️ by TruFindAI Team