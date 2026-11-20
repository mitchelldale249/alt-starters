"""Build the Pokémon data the Starter Trio Finder website uses.

Downloads Pokémon data from PokeAPI's public CSV files and writes
docs/pokemon.json: every unevolved Pokémon that can evolve (rules 2 and 3
in README.md), its final evolutions, and the type chart. The website
applies the remaining rules itself, so their limits can be changed there.

Usage:  python3 scripts/build_data.py
"""
import collections
import csv
import io
import json
import pathlib
import urllib.request

CSV_URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/{}.csv"
ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
OUT = ROOT / "docs" / "pokemon.json"


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

    # Rules 2-3: every unevolved Pokémon that can evolve, with all of its final evolutions.
    # The stat rules (4-7) and the type triangle check (rule 1) run in the browser,
    # so the BST limits can be changed on the website.
    mons, starters = {}, []
    for sid, s in sorted(species.items(), key=lambda kv: int(kv[0])):
        if s["evolves_from_species_id"] or not evolves_into[sid]:
            continue
        finals = final_forms(sid)
        for m in [sid, *finals]:
            i = info(m)
            mons[i["id"]] = [i["name"], i["types"], i["bst"], i["gen"]]
        starters.append([int(sid), [int(f) for f in finals]])

    type_names = sorted({t for ts in poke_types.values() for t in ts})
    chart_out = {a: {d: chart[(a, d)] for d in type_names if chart[(a, d)] != 1} for a in type_names}

    OUT.write_text(json.dumps({"chart": chart_out, "mons": mons, "starters": starters},
                              ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(starters)} unevolved Pokémon that can evolve -> {OUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
