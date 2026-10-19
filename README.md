# Game Match

Application web découplée de recommandation comparée de jeux vidéo.

Projet réalisé dans le cadre de la SAÉ 5.Real.01 du BUT 3 Informatique, IUT de Villetaneuse (Université Sorbonne Paris Nord).

## Présentation

L'utilisateur choisit un jeu vidéo et l'application lui propose des jeux proches, calculés par deux méthodes de recommandation différentes. Les deux listes sont affichées côte à côte avec leurs performances (temps, mémoire, énergie estimée) afin de pouvoir les comparer.

L'application est découplée : le backend (API REST) et le frontend (interface) sont deux projets séparés qui communiquent par HTTP.

## Fonctionnalités prévues

- Recherche et sélection d'un jeu
- Recommandation par similarité de Jaccard (sur les tags)
- Recommandation par embeddings sémantiques (sur les descriptions)
- Affichage des scores de similarité
- Dashboard de comparaison des deux méthodes
- Mesures de performance : temps min / max / moyen / P95, mémoire, impact énergétique estimé, complexité algorithmique

## Méthodes de recommandation

**Jaccard** : on compare les ensembles de tags de deux jeux.
`J(A,B) = |A ∩ B| / |A ∪ B|`
Exemple : {action, combat, hackandslash} et {action, mondeouvert, rpg} ont 1 tag en commun sur 5 distincts, donc J = 0,2.

**Embeddings** : chaque description est transformée en vecteur de 384 dimensions avec le modèle `all-MiniLM-L6-v2` (Sentence Transformers), puis les vecteurs sont comparés par similarité cosinus.

## Dataset

- Steam Games Dataset, Martin Bustos (Fronkon Games), Kaggle
- Licence MIT, 125 855 jeux, données issues de l'API Steam et de SteamSpy
- Choisi parce qu'il contient à la fois une colonne de tags (nécessaire pour Jaccard) et une colonne de description (nécessaire pour les embeddings), avec une licence claire et une mise à jour hebdomadaire
- Le fichier `games.csv` (401 Mo) n'est pas versionné : il faut le télécharger sur Kaggle et le placer dans `backend/data/raw/`
- Un échantillon nettoyé sera généré par un script dans `backend/scripts/`

## Stack technique

| Composant | Technologies |
|---|---|
| Frontend | Vue.js 3, Vite |
| Backend | Python, FastAPI |
| Base de données | SQLite, SQLAlchemy |
| Données | Pandas, NumPy |
| Embeddings | Sentence Transformers |
| Visualisation | Chart.js |
| Tests | Pytest, Vitest |
| Déploiement | Docker |

## Structure du projet