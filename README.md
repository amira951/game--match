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
| Persistance | CSV nettoyé (`games_clean.csv`) lu par Pandas. SQLite prévu pour préférences utilisateur (v0.2) |
| Données | Pandas, NumPy |
| Embeddings | Sentence Transformers |
| Visualisation | Chart.js |
| Tests | Pytest, Vitest |
| Déploiement | Docker |

## Structure du projet

```
game-match/
├── backend/
│   ├── controllers/   routes de l'API
│   ├── services/      algorithmes de recommandation
│   ├── models/        accès aux données
│   ├── scripts/       préparation des données
│   ├── tests/
│   └── data/
├── frontend/
├── docs/
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

Instructions à compléter dès que le backend et le frontend sont en place.

## Organisation Git

- Une branche par membre, nommée `prenom/version`
- Intégration dans `main` par Pull Request après relecture
- Numérotation des versions en semantic versioning (`v0.1.0`, `v0.2.0`, ..., `v1.0.0`)

## Équipe : Les Castors bâtisseurs

- Amira Ben Chaabane
- Kenzo Fillonneau
- Tristan Collen
- Mohamed Flifel
- Elaa Maiz

## Licence

Le code source est sous licence MIT (voir le fichier `LICENSE`). Le dataset est distribué sous sa propre licence MIT par son auteur sur Kaggle.

## Réponses aux remarques du jury

1. Jaccard : approche plate volontaire (tags SteamSpy sans hiérarchie). Amélioration future possible avec taxonomie externe.
2. Granularité : tags nettoyés (minuscule, suppression des très rares <3 occurrences dans l'échantillon). Pas d'enrichissement ChatGPT.
3. Embeddings : description complète utilisée. Isoler gameplay/graphismes possible en pré-traitement, non prioritaire.
4. Dataset : Steam Games Dataset (Martin Bustos, Kaggle, MIT). Un seul dataset pour éviter doublons et risques de format.
5. Volume : échantillon 5000 jeux (triés par avis positifs). Dataset complet disponible.
6. Stack : FastAPI (pas Flask) + Vue.js 3 + Vite. Confirmé.
7. SQLite : remplacé par lecture directe du CSV nettoyé (données statiques Steam). SQLite prévu ultérieurement pour préférences utilisateur (v0.2).
8. Tests : pytest conservés (validation Jaccard). Docker non prioritaire, API REST d'abord.
9. Stratégie : v0.1 = API REST complète (recommandation Jaccard). Interface Vue + dashboard en v0.2.


## État du projet

25/10 : dataset nettoyé (games_clean.csv, 5000 jeux), API Jaccard fonctionnelle (v0.1 backend). Prochaine étape : interface Vue et recherche de jeux.
