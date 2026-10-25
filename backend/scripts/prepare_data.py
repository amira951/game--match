import pandas as pd
from collections import Counter

RAW = "data/raw/games.csv"
OUT = "data/games_clean.csv"
N = 5000

# 1. L'en-tête du CSV a un nom de moins que de colonnes : on le répare
names = list(pd.read_csv(RAW, nrows=0).columns)
i = names.index("DiscountDLC count")
names[i:i+1] = ["Discount", "DLC count"]
df = pd.read_csv(RAW, skiprows=1, header=None, names=names, index_col=False,
                 usecols=["Name", "About the game", "Tags", "Genres", "Header image", "Positive"])
df = df.rename(columns={"Name": "title", "About the game": "description", "Tags": "tags",
                        "Genres": "genres", "Header image": "image", "Positive": "positive"})

# 2. On garde les jeux utilisables par les deux méthodes
df = df.dropna(subset=["title", "description", "tags"])
df = df[df["description"].str.len() > 100]
df = df.drop_duplicates(subset="title")

# 3. Nettoyage des tags : minuscules, puis suppression des tags rares (< 3 occurrences)
df["tags"] = df["tags"].astype(str).str.lower().str.strip()
all_tags = [t.strip() for tags in df["tags"] for t in tags.split(",")]
valid_tags = {t for t, c in Counter(all_tags).items() if c >= 3}
df["tags"] = df["tags"].apply(lambda s: ",".join(t.strip() for t in s.split(",") if t.strip() in valid_tags))
df = df[df["tags"].str.len() > 0]            # retire les jeux sans aucun tag restant

# 4. Nettoyage des descriptions et des genres
df["description"] = df["description"].astype(str).str.replace(r"<[^>]+>", " ", regex=True)
df["description"] = df["description"].str.replace(r"\s+", " ", regex=True).str.strip()
df["genres"] = df["genres"].fillna("")

# 5. Échantillon : les 5000 jeux avec le plus d'avis positifs
df = df.sort_values("positive", ascending=False).head(N).reset_index(drop=True)
df.insert(0, "id", df.index)

df.to_csv(OUT, index=False)
print("Fait :", len(df), "jeux dans", OUT)