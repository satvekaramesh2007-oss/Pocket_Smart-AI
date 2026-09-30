import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.PROJECT_NAME} server...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
