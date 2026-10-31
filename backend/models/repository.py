from pathlib import Path
import pandas as pd

game_data = Path(__file__).resolve().parents[1] / "data" / "games_clean.csv"
users_preferences = Path(__file__).resolve().parents[1] / "data" / "user.db3"


class GameRepository:
    def __init__(self):
        self.df = pd.read_csv(DATA).fillna("")
        self.tag_sets = [set(str(t).split(",")) for t in self.df["tags"]]
        self.engine = create_engine(f"sqlite:///{users_preferences}")


    def count(self): return len(self.df)

    def get(self, i): return self.df.iloc[i].to_dict()

    def all(self): return self.df[["id","title"]].to_dict(orient="records")


    def search(self, q="", limit=20, offset=0):
        df = self.df
        if q:
            df = df[df["title"].str.contains(q, case=False, regex=False)]
        page = df.iloc[offset:offset + limit]
        return {"total": len(df),
                "items": page[["id","title","image","genres"]].to_dict(orient="records")}


    def get_recommendation_based_on_game(self, game_name, top_n=5):
        """
        Ecrite sur kenzo/jaccard cette fonctione permer de récupèrer une liste de jeux similaires à un jeu donné en combinant
        les genres et les tags via l'indice de Jaccard.
        """
        jeu = self.df[self.df["title"].str.lower() == game_name.lower()]

        if jeu.empty:
            return {"error": f"'{game_name}' n'est pas dans le jeu de données"}

        target_idx = jeu.index[0]

        # extraire et nettoyer les genres du jeu cible
        target_genres_str = str(self.df.iloc[target_idx].get("genres", ""))
        target_genres = {g.strip().lower() for g in target_genres_str.split(",") if g.strip()}

        # extraire et nettoyer les tags du jeu cible depuis self.tag_sets
        target_tags = {str(t).strip().lower() for t in self.tag_sets[target_idx] if str(t).strip()}

        scores = []

        # parcourir chaque ligne du DataFrame pour comparer
        for idx, row in self.df.iterrows():
            # ne pas comparer le jeu avec lui-même
            if idx == target_idx:
                scores.append(-1.0) # Score minimal pour l'exclure du top
                continue

            # genres du jeu courant dans le CSV
            game_genres_str = str(row.get("genres", ""))
            game_genres = {g.strip().lower() for g in game_genres_str.split(",") if g.strip()}

            game_tags = {str(t).strip().lower() for t in self.tag_sets[idx] if str(t).strip()}


            if target_genres and game_genres:
                # la logique est expliquer dans la fonction utilisateur
                g_inter = len(target_genres.intersection(game_genres))
                g_union = len(target_genres.union(game_genres))
                genre_score = g_inter / g_union if g_union > 0 else 0.0
            else:
                genre_score = 0.0

            if target_tags and game_tags:
                t_inter = len(target_tags.intersection(game_tags))
                t_union = len(target_tags.union(game_tags))
                tag_score = t_inter / t_union if t_union > 0 else 0.0
            else:
                tag_score = 0.0

            # les genres étant plus généraux , on importe plus d'importance aux tags
            combined_score = (genre_score * 0.4) + (tag_score * 0.6)
            scores.append(combined_score)


        df_scored = self.df.copy()
        df_scored["similarity_score"] = scores

        recommended_df = df_scored.sort_values(by="similarity_score", ascending=False).head(top_n)

        return recommended_df[["id", "title", "image", "genres", "similarity_score"]].to_dict(orient="records")


    def get_recommendation_based_on_user(self,pseudo) :
    """
    Ecrite sur kenzo/jaccarte cette fonction permet de récupérer une liste de jeux qui se rapproche le plus posssible
    des gouts de l'utilisateur'

    """

    genre_query = """
            SELECT DISTINCT g.name
            FROM genres g
            JOIN has_liked_genre hlg ON g.id = hlg.genre_id
        """

    tag_query = """
            SELECT DISTINCT t.name
            FROM tags t
            JOIN has_liked_tags hlt ON t.id = hlt.tag_id
        """

    user_genres_df = pd.read_sql(genre_query, con=self.engine)
    user_genres = set(user_genres_df["name"].str.lower().dropna()) # lower on évite la casse
    # dropna on sup les valeurs vides
    # set pour éliminer les doublons

    user_tags_df = pd.read_sql(tag_query, con=self.engine)
    user_tags = set(user_tags_df["name"].str.lower().dropna())

    jaccarte = []

    for idx, row in self.df.iterrows():
            # genres dans le csv
            game_genres_str = str(row.get("genres", ""))
            game_genres = {g.strip().lower() for g in game_genres_str.split(",") if g.strip()}

            # tag dans le csv
            game_tags_str = str(row.get("tags", ""))
            game_tags = {t.strip().lower() for t in game_tags_str.split(",") if t.strip()}

           # jaccard genre
           if user_genres and game_genres:
                g_inter = len(user_genres.intersection(game_genres)) # user : {'adventure', 'puzzle'} jeu : {'adventure', 'action'} = 1 élément en commun
                g_union = len(user_genres.union(game_genres)) # user : {'adventure', 'puzzle'} jeu : {'adventure', 'action'} = 3 -> {'adventure', 'puzzle' , 'action'}
                genre_score = g_inter / g_union if g_union > 0 else 0.0  #  1 \ 4 = 0.25 donc 25% de similarité
            else:
                genre_score = 0.0

            if user_tags and game_tags:
                t_inter = len(user_tags.intersection(game_tags))
                t_union = len(user_tags.union(game_tags))
                tag_score = t_inter / t_union if t_union > 0 else 0.0
            else:
                tag_score = 0.0





