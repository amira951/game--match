# GameMatch — Frontend Vue 3

Interface Vue 3 + Vite connectée au backend FastAPI du projet.

## Démarrage

Terminal 1 (à la racine du dépôt) :

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Terminal 2 (à la racine du dépôt) :

```powershell
cd frontend
npm install
npm run dev
```

Ouvrir http://localhost:5173.

L'URL de l'API peut être modifiée en créant un fichier `.env` depuis `.env.example`.

## Fonctionnalités

- Recherche par titre via `GET /api/games?search=...`
- Sélection d'un jeu du dataset et affichage des images Steam
- Recommandations Jaccard via `GET /api/recommend/jaccard/{game_id}?k=...`
- Scores et temps d'exécution retournés par le backend
- État de chargement et messages d'erreur si l'API est indisponible
- Interface responsive

La recommandation par embeddings et le dashboard de mesures avancées sont affichés comme fonctionnalités à venir, et non comme fonctionnalités opérationnelles.
