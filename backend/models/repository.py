from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "games_clean.csv"

class GameRepository:
    def __init__(self):
        self.df = pd.read_csv(DATA).fillna("")
        self.tag_sets = [set(str(t).split(",")) for t in self.df["tags"]]
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