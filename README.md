# alt-starters

A website showing alternate possible starter combinations for Pokémon that follow the rock/paper/scissors criteria without being constrained to the usual Water/Fire/Grass typings.

## The rules

A trio of Pokémon is a valid starter trio when:

1. Each Pokémon has one type advantage and one type disadvantage against the others in the trio, and their final evolutions keep the same loop
2. Each Pokémon is unevolved
3. Each Pokémon can evolve at least once
4. Each Pokémon has a base stat total (BST) of 325 or less
5. Each Pokémon's final evolution has a BST of 475 or more
6. The starters' BSTs differ by no more than 20
7. The final evolutions' BSTs differ by no more than 30

The numbers in rules 4 to 7 can be changed on the website. Edit them in the rules box and the list updates straight away. Starter BSTs go up to 600 and spreads up to 50, so the calculation stays quick.

How the rules are applied:

- **Type advantage:** A has the advantage over B when at least one of A's types is super effective against B, counting both of B's types. The trio must form a one-way loop (A beats B, B beats C, C beats A) with no advantage running the other way. Their final evolutions must form the same loop. Uses the current type chart, including Fairy.
- **Unevolved** means the first stage of an evolution line, so Pichu counts and Pikachu does not.
- Only each species' standard form is included (no regional forms).
- **Branching evolutions:** when a line branches, like Poliwag into Poliwrath or Politoed, rules 5 and 7 use its highest-BST final evolution. Every final evolution must keep the type loop (rule 1) in every combination with the other two Pokémon. Each trio appears once, listing all of its final evolutions whatever their BST.

## Project layout

| Path | What it is |
| --- | --- |
| `scripts/build_data.py` | Downloads Pokémon data from [PokeAPI](https://pokeapi.co/) and writes `docs/pokemon.json` |
| `docs/pokemon.json` | Every unevolved Pokémon that can evolve, its final evolutions, and the type chart |
| `docs/index.html` | The website. It applies the rules to `pokemon.json` in the browser, which is what lets you change the stat limits |

## Updating the data

Requires Python 3, no extra packages:

```bash
python3 scripts/build_data.py
```

Downloaded data is cached in `.cache/`. Delete that folder to fetch fresh data, for example after new Pokémon are released.

## Viewing the site locally

The page loads `pokemon.json`, which browsers block when you open the file directly, so serve the folder instead:

```bash
python3 -m http.server --directory docs 8000
```

Then open http://localhost:8000.

## Publishing with GitHub Pages

In the repository's **Settings → Pages**, set **Source** to "Deploy from a branch", choose the `main` branch and the `/docs` folder, and save. The site appears at `https://<your-username>.github.io/alt-starters/` after a minute or two.

---

Pokémon and Pokémon character names are trademarks of Nintendo, Game Freak and Creatures. This is an unofficial fan project.
