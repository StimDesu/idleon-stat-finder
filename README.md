# IdleOn Stat Finder

Pick a stat in Legends of Idleon (drop rate, cooking speed, lab line width, mining efficiency…) and see every
bonus in the game that raises it, grouped by system: talents, bubbles, vials, stamps, cards, statues, star signs,
meals, lab jewels, vault, caverns and ~60 more. EN / RU. Free-text search over all bonus texts.

Everything is read from the game code (`N.js` inside the Steam build); nothing is typed in by hand except the
stat list and its search patterns. `#` in a text marks the number the game fills in (it depends on the level).

## Update after a game patch

    python tools/extract.py      # reads the installed game -> src/data.json, img/favicon.png; prints hits per stat
    python build.py              # src/template.html + src/data.json -> index.html

- `tools/extract.py` — `SOURCES` maps each game list to a system name (EN/RU), the column with the name and the
  columns with bonus texts. Talents, alchemy, cards, stamps and gear have their own readers.
- `tools/stats.py` — the stat list, grouped by meaning. Each stat is a regex over the English text plus an
  optional `not` regex for look-alike texts. Add a stat, rerun, check the printed count and the page.
- Russian texts come from the [IdleOn-Rusificator](https://github.com/StimDesu/IdleOn-Rusificator) dictionaries.

Part of [IdleOn miniToolBox](https://github.com/StimDesu/idleon-minitoolbox).
