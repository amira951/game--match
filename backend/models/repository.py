from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "games_clean.csv"

class GameRepository:
    def __init__(self):
        self.df = pd.read_csv(DATA)
        self.tag_sets = [set(str(t).split(",")) for t in self.df["tags"]]
    def count(self): return len(self.df)
    def get(self, i): return self.df.iloc[i].to_dict()
    def all(self): return self.df[["id","title"]].to_dict(orient="records")