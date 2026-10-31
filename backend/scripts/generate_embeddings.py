import time
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

DATA = Path(__file__).resolve().parents[1] / "data"
CSV = DATA / "games_clean.csv"
OUT = DATA / "embeddings.npy"
MODEL = "all-MiniLM-L6-v2"

df = pd.read_csv(CSV).fillna("")
if not (df["id"].to_numpy() == np.arange(len(df))).all():
    raise SystemExit("Les id du CSV doivent valoir 0, 1, 2, ... dans l'ordre des lignes.")

t0 = time.perf_counter()
model = SentenceTransformer(MODEL)
print(f"Modèle chargé en {time.perf_counter() - t0:.1f} s")

t0 = time.perf_counter()
emb = model.encode(
    df["description"].astype(str).tolist(),
    batch_size=64,
    show_progress_bar=True,
    normalize_embeddings=True,
    convert_to_numpy=True,
).astype("float32")
print(f"{len(df)} descriptions encodées en {time.perf_counter() - t0:.1f} s")

np.save(OUT, emb)
print(f"Fichier écrit : {OUT} (forme {emb.shape})")
