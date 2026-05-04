# Déploiement GitHub + Vercel + Railway

## 1. GitHub
Upload tout le contenu de ce ZIP dans ton repo. Tu dois voir à la racine :

```text
frontend/
backend/
README.md
GEMINI_SETUP.md
DEPLOYMENT_GUIDE.md
```

Ne mets jamais ta vraie clé Gemini dans GitHub.

## 2. Vercel frontend
- Import GitHub repo
- Root Directory: `frontend`
- Build command: `npm run build`
- Output directory: `build`
- Environment variable:
  - `REACT_APP_BACKEND_URL=https://ton-backend-url`

## 3. Railway backend
- New Project → Deploy from GitHub
- Root Directory: `backend`
- Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `GEMINI_API_KEY=...`
  - `MONGO_URL=...`
  - `DB_NAME=autosite`
  - `CORS_ORIGINS=https://ton-frontend-url.vercel.app`

## 4. MongoDB
Tu peux utiliser MongoDB Atlas gratuitement au début. Copie l'URL de connexion dans `MONGO_URL`.
