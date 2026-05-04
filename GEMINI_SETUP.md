# AutoSite AI Pro — Version Gemini Boost

Cette version remplace Emergent par Gemini et renforce la qualité du rendu.

## 1. Créer `backend/.env`

Copie `backend/.env.example` vers `backend/.env`, puis ajoute ta clé :

```env
GEMINI_API_KEY=ta_cle_gemini
GEMINI_MODEL=gemini-1.5-flash
MONGO_URL=mongodb://localhost:27017
DB_NAME=autosite
CORS_ORIGINS=*
```

## 2. Installer backend

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

## 3. Lancer frontend

```bash
cd frontend
npm install
npm run dev
```

## Ce qui est boosté

- Prompt Gemini beaucoup plus premium.
- Sortie JSON plus stable et mieux contrôlée.
- Fallback automatique si Gemini oublie un champ.
- Ajout de sections premium : trust bar, process, direction artistique.
- Rendu HTML plus haut de gamme avec carte signature, orb glow, animations et microcopy.
- SEO local renforcé.
