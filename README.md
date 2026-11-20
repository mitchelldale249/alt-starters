# alt-starters

A website showing alternate possible starter combinations for Pokémon that follow the rock/paper/scissors criteria without being constrained to the usual Water/Fire/Grass typings.

## The rules

A trio of Pokémon is a valid starter trio when:

1. Each Pokémon has one type advantage and one type disadvantage against the others in the trio
2. Each Pokémon is unevolved
3. Each Pokémon can evolve at least once
4. Each Pokémon has a base stat total (BST) of 350 or less
5. Each Pokémon's final evolution has a BST of 450 or more
6. The starters' BSTs differ by no more than 10
7. The final evolutions' BSTs differ by no more than 10

How the rules are applied:

- **Type advantage:** A has the advantage over B when at least one of A's types is super effective against B, counting both of B's types. The trio must form a one-way loop (A beats B, B beats C, C beats A) with no advantage running the other way. Uses the current type chart, including Fairy.
- **Unevolved** means the first stage of an evolution line, so Pichu counts and Pikachu does not.
- Only each species' standard form is included (no regional forms).
- When an evolution line branches, each final evolution is checked separately, so a trio can appear more than once with different final forms.

## Project layout

| Path | What it is |
| --- | --- |
| `scripts/find_trios.py` | Downloads Pokémon data from [PokeAPI](https://pokeapi.co/), applies the rules and writes `docs/trios.json` |
| `docs/index.html` | The website |
| `docs/trios.json` | The list of valid trios the website shows |

## Updating the data

Requires Python 3, no extra packages:

```bash
python3 scripts/find_trios.py
```

Downloaded data is cached in `.cache/`. Delete that folder to fetch fresh data, for example after new Pokémon are released.

## Viewing the site locally

The page loads `trios.json`, which browsers block when you open the file directly, so serve the folder instead:

```bash
python3 -m http.server --directory docs 8000
```

Then open http://localhost:8000.

## Publishing with GitHub Pages

In the repository's **Settings → Pages**, set **Source** to "Deploy from a branch", choose the `main` branch and the `/docs` folder, and save. The site appears at `https://<your-username>.github.io/alt-starters/` after a minute or two.

---

Pokémon and Pokémon character names are trademarks of Nintendo, Game Freak and Creatures. This is an unofficial fan project.
