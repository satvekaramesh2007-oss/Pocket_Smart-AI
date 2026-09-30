# PocketSmart AI – Your Smart Budget & Recommendation Assistant ⚡

PocketSmart AI is a production-style, GenAI-powered web application built with **FastAPI**, **Jinja2**, **Vanilla CSS & JS**, **SQLite (SQLAlchemy ORM)**, and the official **Google GenAI SDK (`google-genai`)**. 

It empowers users to plan **Home Interior Design**, **Party & Event Celebrations**, and **Jewelry Styling** while strictly adhering to user-defined budget constraints.

---

## 🌟 Key Features

1. **🏠 Home Interior Planner**: Calculates category budget splits (furniture, lighting, rugs, decor) and suggests items matching room types (Living Room, Bedroom, Study) and styles (Modern, Minimalist, Luxury).
2. **🎉 Party & Event Planner**: Intelligently allocates event budgets across venue rental, food catering, theme decoration, and entertainment for birthdays, weddings, or corporate events.
3. **💎 Jewelry Recommendation Assistant**: Accepts optional outfit photo uploads (`.jpg`, `.png`, `.webp`) and performs multimodal visual analysis (color harmony, neckline compatibility) to suggest matching necklaces, earrings, and bangles.
4. **💰 Strict Budget Engine**: Tags plan items as `Within Budget`, `Near Budget`, or `Over Budget`. Automatically calculates cheaper alternative suggestions if budget limits are exceeded.
5. **🔒 Secure JWT & Cookie Authentication**: Registration, Login, Logout, bcrypt password hashing, and protected dashboard/planner routes.
6. **⚡ Seamless Demo Mode Fallback**: If no Gemini API key is configured or external APIs fail, PocketSmart AI automatically operates in **Demo Mode** using realistic local catalog recommendation data.
7. **📜 Plan History & Saved Items**: Save favorite recommendation plans, reopen detailed budget breakdowns, or delete old plans.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy ORM
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism design system), JavaScript (AJAX, Toast notifications), Jinja2 Templates
- **AI Integration**: Google GenAI SDK (`google-genai` / `gemini-2.5-flash`), PIL Multimodal Image Processing
- **Storage**: SQLite (`pocketsmart.db`) with modular database abstraction
- **Security**: PyJWT, bcrypt / passlib, HTTP-only Cookie handling
- **Testing**: Pytest & FastAPI TestClient

---

## 📁 Directory Structure

```text
pocketsmart-ai/
│
├── app/
│   ├── main.py                   # FastAPI app instance, CORS, static mounting
│   ├── config.py                 # Pydantic environment configuration
│   ├── database.py               # SQLAlchemy SQLite connection engine
│   │
│   ├── models/                   # SQLAlchemy ORM Models
│   │   ├── user.py               # User table
│   │   ├── planner.py            # PlannerRequest table
│   │   └── recommendation.py     # Recommendation & SavedItem tables
│   │
│   ├── schemas/                  # Pydantic Schemas
│   │   ├── auth.py               # UserRegister, UserLogin, Token
│   │   ├── home.py               # HomePlannerRequest
│   │   ├── party.py              # PartyPlannerRequest
│   │   ├── jewelry.py            # JewelryPlannerRequest
│   │   └── recommendation.py     # RecommendationResponse & History
│   │
│   ├── routes/                   # API & Web View Controllers
│   │   ├── auth.py               # Register, Login, Logout, Session endpoints
│   │   ├── home.py               # POST /generate-home
│   │   ├── party.py              # POST /generate-party
│   │   ├── jewelry.py            # POST /generate-jewelry (Multimodal image upload)
│   │   ├── recommendations.py    # GET/DELETE recommendations, POST save
│   │   ├── history.py            # GET /api/history
│   │   └── views.py              # HTML Page template render routes
│   │
│   ├── services/                 # Business & AI Logic Services
│   │   ├── auth_service.py       # Password hashing & JWT token validation
│   │   ├── budget_service.py     # Budget breakdown formulas & local catalog
│   │   ├── gemini_service.py     # Google GenAI SDK wrapper & fallback engine
│   │   └── recommendation_service.py # Orchestrator & DB persistence
│   │
│   ├── templates/                # Jinja2 HTML Templates
│   │   ├── base.html             # Master layout with Navbar & Loading overlay
│   │   ├── index.html            # Landing page
│   │   ├── login.html            # Login form
│   │   ├── register.html         # Registration form
│   │   ├── dashboard.html        # User dashboard & statistics
│   │   ├── home_planner.html     # Home planner form
│   │   ├── party_planner.html    # Party planner form
│   │   ├── jewelry_planner.html  # Jewelry planner form with image upload
│   │   ├── results.html          # Detailed recommendation results
│   │   └── history.html          # Plan history & saved items grid
│   │
│   └── static/
│       ├── css/
│       │   └── style.css         # Glassmorphism dark mode CSS design system
│       └── js/
│           └── app.js            # AJAX submit, toast notifications & image previewer
│
├── uploads/                      # Temporary outfit image upload directory
├── tests/                        # Pytest automated test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_planners.py
│   ├── test_budget.py
│   ├── test_recommendations.py
│   └── test_health.py
│
├── .env                          # Environment secrets configuration
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt              # Python dependencies list
├── README.md                     # Comprehensive documentation
└── run.py                        # Uvicorn server launcher
```

---

## ⚙️ Setup & Installation Instructions

### 1. Prerequisites
- Python 3.9 or higher installed.

### 2. Create and Activate Virtual Environment

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration (`.env`)

Create a `.env` file in the project root directory (or copy `.env.example`):

```ini
PROJECT_NAME="PocketSmart AI"
SECRET_KEY="pocketsmart-super-secret-jwt-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Leave GEMINI_API_KEY blank to run in Demo Mode by default
GEMINI_API_KEY="your_google_gemini_api_key_here"
GEMINI_MODEL="gemini-2.5-flash"
DEMO_MODE=false

DATABASE_URL="sqlite:///./pocketsmart.db"
UPLOAD_DIR="./uploads"
MAX_IMAGE_SIZE_MB=5
```

> 💡 **Note on Demo Mode**: If `GEMINI_API_KEY` is not supplied or `DEMO_MODE=true` is set, the application will display a **⚡ DEMO MODE** badge and generate intelligent mock recommendations using local catalog datasets.

---

## 🚀 Running the Application

Start the development server using either `run.py` or `uvicorn`:

```bash
python run.py
```
*or*
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Running Automated Tests

Run the complete pytest test suite:

```bash
pytest -v
```

---

## 🌐 API Route Endpoint Summary

| Method | Endpoint | Description | Protected |
| :--- | :--- | :--- | :---: |
| `GET` | `/` | Landing page view | ❌ |
| `GET` | `/login` | User login view | ❌ |
| `GET` | `/register` | User registration view | ❌ |
| `POST` | `/register` | Register new account API | ❌ |
| `POST` | `/login` | Authenticate user & set JWT cookie | ❌ |
| `GET` | `/logout` | Logout user & clear cookie | ❌ |
| `GET` | `/dashboard` | User dashboard view | 🔑 |
| `GET` | `/home-planner` | Home planner form view | 🔑 |
| `POST` | `/generate-home` | Generate home recommendations | 🔑 |
| `GET` | `/party-planner` | Party planner form view | 🔑 |
| `POST` | `/generate-party` | Generate party recommendations | 🔑 |
| `GET` | `/jewelry-planner` | Jewelry planner form view | 🔑 |
| `POST` | `/generate-jewelry` | Multimodal jewelry styling API | 🔑 |
| `GET` | `/results/{id}` | Detailed results view | 🔑 |
| `GET` | `/history` | User plan history view | 🔑 |
| `GET` | `/recommendations/{id}` | Fetch plan JSON by ID | 🔑 |
| `POST` | `/recommendations/{id}/save` | Toggle save/bookmark plan | 🔑 |
| `DELETE` | `/recommendations/{id}` | Delete recommendation plan | 🔑 |
| `GET` | `/health` | Application health check | ❌ |

---

## 🛡️ License

Built with ❤️ for AI developers and college project demonstrations.
