# AutoSite AI Pro — GitHub Ready

Structure propre pour déploiement :

- `frontend/` : React app
- `backend/` : FastAPI + Gemini + MongoDB

## Backend environment variables
Do not commit a real `.env` file. Add these variables in Railway/Render:

```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URL=your_mongodb_connection_string
DB_NAME=autosite
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

## Frontend environment variables
Add this in Vercel:

```env
REACT_APP_BACKEND_URL=https://your-backend-domain.railway.app
```

## Local run

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm start
```
