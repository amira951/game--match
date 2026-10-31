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





