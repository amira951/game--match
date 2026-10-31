import argparse
import collections
import os
import re
import sqlite3
import statistics
import tempfile
import time
import tracemalloc

import pandas as pd


def run(fn, reps):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        ts.append((time.perf_counter() - t0) * 1000)
    ts.sort()
    return statistics.median(ts), ts[int(0.95 * (len(ts) - 1))]


def peak_mb(fn, runs=3):
    peaks = []
    for _ in range(runs):
        tracemalloc.start()
        fn()
        peaks.append(tracemalloc.get_traced_memory()[1] / 1e6)
        tracemalloc.stop()
    return statistics.median(peaks)


def to_sets(ids, tags):
    return {i: {t.strip() for t in str(s).split(",") if t.strip()} for i, s in zip(ids, tags)}


def jaccard_top10(tags_by_id, ref_id):
    ref = tags_by_id[ref_id]
    out = []
    for gid, tags in tags_by_id.items():
        if gid != ref_id:
            u = len(ref | tags)
            out.append((len(ref & tags) / u if u else 0.0, gid))
    out.sort(reverse=True)
    return out[:10]


def scale(df, n):
    reps = -(-n // len(df))
    big = pd.concat([df] * reps, ignore_index=True).head(n).copy()
    big["id"] = range(1, n + 1)
    big["title"] = [f"{t} #{i}" if i > len(df) else t for i, t in zip(big["id"], big["title"])]
    return big


def pick_term(df):
    words = collections.Counter(
        w for t in df["title"].astype(str) for w in set(re.findall(r"[a-z]{4,}", t.lower())))
    target = max(5, len(df) // 100)
    return min(words.items(), key=lambda kv: abs(kv[1] - target))[0]


def bench(base, n, term, workdir, reps, heavy):
    big = scale(base, n)
    cols = ["id", "title", "description", "tags"]
    csv_path = os.path.join(workdir, f"g{n}.csv")
    db_path = os.path.join(workdir, f"g{n}.db")
    big[cols].to_csv(csv_path, index=False)
    con = sqlite3.connect(db_path)
    try:
        big[cols].to_sql("games", con, index=False, if_exists="replace")
        con.execute("CREATE INDEX idx_id ON games(id)")
        con.execute("CREATE INDEX idx_title ON games(title COLLATE NOCASE)")
        con.commit()
    finally:
        con.close()
    r = {"jeux": n,
         "taille_csv_Mo": round(os.path.getsize(csv_path) / 1e6, 1),
         "taille_db_Mo": round(os.path.getsize(db_path) / 1e6, 1)}
    target = int(big["id"].iloc[n // 2])

    def tags_csv():
        d = pd.read_csv(csv_path, usecols=["id", "tags"])
        return to_sets(d["id"], d["tags"])

    def tags_sql():
        c = sqlite3.connect(db_path)
        rows = c.execute("SELECT id, tags FROM games").fetchall()
        c.close()
        return to_sets([x[0] for x in rows], [x[1] for x in rows])

    def all_csv():
        d = pd.read_csv(csv_path)
        return d.set_index("id", drop=False)

    def all_sql():
        c = sqlite3.connect(db_path)
        d = pd.read_sql("SELECT * FROM games", c)
        c.close()
        return d.set_index("id", drop=False)

    r["demarrage_tags_csv_ms"] = round(run(tags_csv, heavy)[0])
    r["demarrage_tags_sqlite_ms"] = round(run(tags_sql, heavy)[0])
    r["demarrage_tout_csv_ms"] = round(run(all_csv, heavy)[0])
    r["demarrage_tout_sqlite_ms"] = round(run(all_sql, heavy)[0])
    r["memoire_tags_csv_Mo"] = round(peak_mb(tags_csv), 1)
    r["memoire_tags_sqlite_Mo"] = round(peak_mb(tags_sql), 1)

    d = all_csv()
    tags_by_id = tags_csv()
    c = sqlite3.connect(db_path)
    like = f"%{term}%"

    def q(name, fn_csv, fn_sql):
        m, p = run(fn_csv, reps); r[f"{name}_csv_ms"] = round(m, 3); r[f"{name}_csv_p95"] = round(p, 3)
        m, p = run(fn_sql, reps); r[f"{name}_sqlite_ms"] = round(m, 3); r[f"{name}_sqlite_p95"] = round(p, 3)

    q("id",
      lambda: d.loc[target].to_dict(),
      lambda: c.execute("SELECT * FROM games WHERE id = ?", (target,)).fetchone())
    q("titre_20premiers",
      lambda: d.loc[d["title"].str.contains(term, case=False, regex=False, na=False), ["id", "title"]].head(20),
      lambda: c.execute("SELECT id, title FROM games WHERE title LIKE ? LIMIT 20", (like,)).fetchall())
    q("titre_tous",
      lambda: int(d["title"].str.contains(term, case=False, regex=False, na=False).sum()),
      lambda: c.execute("SELECT COUNT(*) FROM games WHERE title LIKE ?", (like,)).fetchone())
    q("titre_debut",
      lambda: d.loc[d["title"].str.lower().str.startswith(term, na=False), ["id", "title"]].head(20),
      lambda: c.execute("SELECT id, title FROM games WHERE title LIKE ? LIMIT 20", (f"{term}%",)).fetchall())

    r["reco_RAM_ms"] = round(run(lambda: jaccard_top10(tags_by_id, target), heavy)[0])
    r["reco_relit_csv_ms"] = round(run(lambda: jaccard_top10(tags_csv(), target), heavy)[0])
    r["reco_relit_sqlite_ms"] = round(run(lambda: jaccard_top10(tags_sql(), target), heavy)[0])
    r["premiere_reco_csv_ms"] = round(run(lambda: jaccard_top10(tags_csv(), target), heavy)[0])
    r["premiere_reco_sqlite_ms"] = round(run(lambda: jaccard_top10(tags_sql(), target), heavy)[0])
    c.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--sizes", type=int, nargs="+", default=[5000, 25000, 100000])
    ap.add_argument("--reps", type=int, default=100, help="répétitions des requêtes rapides")
    ap.add_argument("--heavy", type=int, default=5, help="répétitions des opérations lourdes")
    a = ap.parse_args()

    df = pd.read_csv(a.csv).dropna(subset=["title", "tags"]).reset_index(drop=True)
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)
    if "description" not in df.columns:
        df["description"] = ""
    df["description"] = df["description"].fillna("")
    term = pick_term(df)
    print(f"Jeux réels : {len(df)} | mot de recherche : '{term}' (identique pour toutes les tailles)", flush=True)

    rows = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as wd:
        for n in a.sizes:
            print(f"... {n} jeux", flush=True)
            rows.append(bench(df, n, term, wd, a.reps, a.heavy))
    out = pd.DataFrame(rows).set_index("jeux").T
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 200)
    print("\n", out.to_string())
    out.to_csv("benchmark_results.csv")
    print("\nRésultats écrits dans benchmark_results.csv")
    print("Limites : une seule machine ; tailles > jeux réels simulées par répétition.")


if __name__ == "__main__":
    main()