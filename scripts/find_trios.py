"""Find every Pokémon trio that could work as an alternative starter trio.

Downloads Pokémon data from PokeAPI's public CSV files, applies the seven
starter rules (see README.md) and writes the results to docs/trios.json,
which the website reads.

Usage:  python3 scripts/find_trios.py
"""
import collections
import csv
import io
import itertools
import json
import pathlib
import urllib.request

CSV_URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/{}.csv"
ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
OUT = ROOT / "docs" / "trios.json"

MAX_STARTER_BST = 350   # rule 4
MIN_FINAL_BST = 450     # rule 5
MAX_STARTER_SPREAD = 10 # rule 6
MAX_FINAL_SPREAD = 10   # rule 7


def table(name):
    """Read one PokeAPI CSV table, downloading it into .cache/ the first time."""
    path = CACHE / f"{name}.csv"
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        with urllib.request.urlopen(CSV_URL.format(name)) as resp:
            path.write_bytes(resp.read())
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def main():
    types = {t["id"]: t["identifier"] for t in table("types")}
    chart = collections.defaultdict(lambda: 1.0)
    for e in table("type_efficacy"):
        chart[(types[e["damage_type_id"]], types[e["target_type_id"]])] = int(e["damage_factor"]) / 100

    species = {s["id"]: s for s in table("pokemon_species")}
    names = {n["pokemon_species_id"]: n["name"]
             for n in table("pokemon_species_names") if n["local_language_id"] == "9"}  # English
    default_form = {p["species_id"]: p["id"] for p in table("pokemon") if p["is_default"] == "1"}
    bst = collections.Counter()
    for s in table("pokemon_stats"):
        bst[s["pokemon_id"]] += int(s["base_stat"])
    poke_types = collections.defaultdict(list)
    for t in sorted(table("pokemon_types"), key=lambda t: int(t["slot"])):
        poke_types[t["pokemon_id"]].append(types[t["type_id"]])

    evolves_into = collections.defaultdict(list)
    for s in species.values():
        if s["evolves_from_species_id"]:
            evolves_into[s["evolves_from_species_id"]].append(s["id"])

    def info(sid):
        pid = default_form[sid]
        return {"id": int(sid), "name": names[sid], "types": poke_types[pid],
                "bst": bst[pid], "gen": int(species[sid]["generation_id"])}

    def final_forms(sid):
        kids = evolves_into[sid]
        return [sid] if not kids else [f for k in kids for f in final_forms(k)]

    # Rules 2-5: unevolved, can evolve, BST <= 350, a final evolution with BST >= 450.
    candidates = []
    for sid, s in species.items():
        if s["evolves_from_species_id"] or not evolves_into[sid]:
            continue
        base = info(sid)
        if base["bst"] > MAX_STARTER_BST:
            continue
        finals = [info(f) for f in final_forms(sid)]
        finals = [f for f in finals if f["bst"] >= MIN_FINAL_BST]
        if finals:
            candidates.append((base, finals))

    def beats(a, b):
        """A has the advantage if any of A's types is super effective against B."""
        def mult(t):
            m = 1.0
            for target in b["types"]:
                m *= chart[(t, target)]
            return m
        return any(mult(t) > 1 for t in a["types"])

    trios = []
    for (a, fa), (b, fb), (c, fc) in itertools.combinations(candidates, 3):
        if max(a["bst"], b["bst"], c["bst"]) - min(a["bst"], b["bst"], c["bst"]) > MAX_STARTER_SPREAD:
            continue  # rule 6
        # Rule 1: a one-way loop x > y > z > x with no advantage running backwards.
        loop = None
        for x, y, z in ((a, b, c), (a, c, b)):
            if beats(x, y) and beats(y, z) and beats(z, x) and not (beats(y, x) or beats(z, y) or beats(x, z)):
                loop = (x, y, z)
        if not loop:
            continue
        finals_of = {a["id"]: fa, b["id"]: fb, c["id"]: fc}
        for finals in itertools.product(*(finals_of[m["id"]] for m in loop)):
            totals = [f["bst"] for f in finals]
            if max(totals) - min(totals) <= MAX_FINAL_SPREAD:  # rule 7
                trios.append([m["id"] for m in loop] + [f["id"] for f in finals])

    mons = {}
    for base, finals in candidates:
        for m in [base, *finals]:
            mons[m["id"]] = [m["name"], m["types"], m["bst"], m["gen"]]
    used = {i for t in trios for i in t}
    mons = {k: v for k, v in sorted(mons.items()) if k in used}

    OUT.write_text(json.dumps({"mons": mons, "trios": trios}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(candidates)} eligible starters, {len(trios)} valid trios -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
