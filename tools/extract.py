"""Builds src/data.json: every bonus source in the game code, with names, and which stats each one raises.

    python tools/extract.py [--game "<Legends of Idleon folder>"] [--ru <IdleOn-Rusificator/translation>]

Game data lives in N.js as `X.<List>=function(){return [...]}` literals (read from resources/app.asar).
Each list in SOURCES below is a game system (bubbles, statues, vault upgrades...). Its rows give a name and
one or more bonus texts like "+{%_Meal_Cooking_Speed" ({ } $ are the numbers the game fills in).
A few systems need their names from elsewhere and have their own readers (talents, cards, stamps, gear).
Every text is then matched against the stat list in tools/stats.py; the page shows the matches grouped by system.
Russian names and texts come from the IdleOn-Rusificator dictionaries (same raw keys as the game).
"""
import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from gamecode import read_game, literal  # noqa: E402
import items as itemdefs  # noqa: E402
from stats import CATEGORIES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# list -> (system EN, system RU, name index or None, text indexes or None = every text-like string of the row)
# A system shows up in the results under its label; the order here is the order on the page.
SOURCES = [
    ("StarSigns", "Star signs", "Знаки зодиака", 0, [1, 2, 3]),
    ("StatueInfo", "Statues", "Статуи", 0, [1]),
    ("ShrineInfo", "Shrines", "Святилища", 0, [1]),
    ("PostOffUpgradeInfo", "Post office boxes", "Почтовые ящики", 0, [4, 8, 12]),
    ("GuildBonuses", "Guild bonuses", "Бонусы гильдии", 0, [3]),
    ("ClassFamilyBonuses", "Family bonuses (class)", "Семейные бонусы (класс)", None, [0]),
    ("ArcadeShopInfo", "Arcade shop", "Магазин аркады", None, [0]),
    ("BribeDescriptions", "Bribes", "Взятки", 0, [1]),
    ("TaskShopDesc", "Task merit shop", "Магазин заслуг (задания)", None, "task"),
    ("RegAchieves", "Achievements", "Достижения", 0, [3]),
    ("CardSets", "Card sets", "Наборы карт", None, [0]),
    ("SigilDesc", "Alchemy sigils", "Сигилы алхимии", 0, [6]),
    ("PrayerInfo", "Prayers (bonus)", "Молитвы (бонус)", 0, [1]),
    ("TDtraits", "Worship tower defence", "Поклонение: оборона", None, [0, 3]),
    ("CaptainBonuses", "Sailing captains", "Капитаны (плавание)", None, [3]),
    ("ArtifactInfo", "Sailing artifacts", "Артефакты (плавание)", 0, None),
    ("GodsInfo", "Divinity gods", "Боги (божественность)", 0, [1, 2, 6]),
    ("JewelDesc", "Lab jewels", "Самоцветы лаборатории", 11, [3]),
    ("LabMainBonus", "Lab mainframe", "Мейнфрейм лаборатории", 6, [7]),
    ("ChipDesc", "Lab chips", "Чипы лаборатории", 0, [1]),
    ("PetUpgradeINFO", "Breeding upgrades", "Улучшения разведения", 0, [9, 10]),
    ("MealINFO", "Meals", "Блюда", 0, [3]),
    ("TowerInfo", "Construction buildings", "Постройки (строительство)", 0, [1]),
    ("SaltLicks", "Salt lick", "Солонец", None, [1]),
    ("AtomInfo", "Atom collider", "Коллайдер атомов", 0, [5]),
    ("MarketInfo", "Farming: market", "Фермерство: рынок", 0, [1]),
    ("MarketExoticInfo", "Farming: exotic market", "Фермерство: экзотический рынок", 0, [1]),
    ("NinjaUpg", "Sneaking: ninja knowledge", "Скрытность: знания ниндзя", 4, [6]),
    ("NinjaInfo", "Sneaking: other bonuses", "Скрытность: прочие бонусы", None, None),
    ("SummonUPG", "Summoning upgrades", "Улучшения призыва", 3, [11]),
    ("GamingUpg", "Gaming: upgrades", "Игры: улучшения", 3, [0]),
    ("GamingPalette", "Gaming: palette", "Игры: палитра", 3, [10]),
    ("GamingUpgrades", "Gaming: sprouts", "Игры: ростки", 0, [5]),
    ("DreamUpg", "Equinox dreams", "Сны равноденствия", 0, [1]),
    ("UpgradeVault", "Upgrade vault", "Хранилище улучшений", 0, [9]),
    ("CompassUpg", "Compass (Wind Walker)", "Компас (Wind Walker)", 0, [11]),
    ("GrimoireUpg", "Grimoire (Death Bringer)", "Гримуар (Death Bringer)", 0, [9]),
    ("ArcaneUpg", "Tesseract (Arcane Cultist)", "Тессеракт (Arcane Cultist)", 0, [9]),
    ("LegendTalents", "Legend talents", "Легендарные таланты", 0, [5]),
    ("HolesBuildings", "Caverns: villager buildings", "Пещеры: постройки", 0, [5]),
    ("HoleFountUPG", "Caverns: fountain", "Пещеры: фонтан", 0, [7]),
    ("CosmoUpgrades", "Caverns: cosmos", "Пещеры: космос", 2, [3]),
    ("LampWishes", "Caverns: lamp wishes", "Пещеры: желания лампы", 0, [4]),
    ("HolesInfo", "Caverns: other bonuses", "Пещеры: прочие бонусы", None, None),
    ("ArmoryUpg", "Armory", "Оружейная", 0, [9]),
    ("SushiUPG", "Sushi station", "Суши-станция", 0, [5]),
    ("JellyUPG", "Jelly operator", "Желе-оператор", 0, [5]),
    ("BubbaUpg", "Bubba", "Бубба", 0, [7]),
    ("MineheadUPG", "Minehead", "Minehead", 0, [5]),
    ("SpelunkUpg", "Spelunking upgrades", "Спелеология: улучшения", 0, [12]),
    ("SpelunkChapters", "Spelunking lore", "Спелеология: книга", None, None),
    ("Spelunky", "Spelunking: other bonuses", "Спелеология: прочие бонусы", None, None),
    ("OrbletMarket", "Zenith: orblet market", "Зенит: рынок орблетов", 0, [6]),
    ("ZenithMarket", "Zenith market", "Рынок зенита", 0, [6]),
    ("EmperorBon", "Emperor bonuses", "Бонусы императора", None, None),
    ("CoralReef", "Coral reef", "Коралловый риф", None, [0]),
    ("Owlz", "Orion the owl", "Сова Орион", 0, [4, 5]),
    ("ResGridSquares", "Research grid", "Сетка исследований", 0, [5]),
    ("Research", "Research: other bonuses", "Исследования: прочие бонусы", None, None),
    ("RANDOlist", "Other bonuses (misc lists)", "Прочие бонусы (разные списки)", None, None),
    ("RandoListo2", "Other bonuses (misc lists)", "Прочие бонусы (разные списки)", None, None),
]
SKIP = {"Filler", "filler", "Blank", "txt", "Name", "desc", "Nothing_yet..."}
LETTERS = re.compile(r"[A-Za-z].*[A-Za-z].*[A-Za-z]")


def is_text(s):
    return isinstance(s, str) and s not in SKIP and ("_" in s or " " in s) and LETTERS.search(s) \
        and not re.fullmatch(r"[\d,;.\- ]+", s)


def rows(v):
    """Innermost lists that hold strings."""
    if isinstance(v, list):
        if any(isinstance(x, str) for x in v):
            yield v
        for x in v:
            if isinstance(x, list):
                yield from rows(x)


def clean(s):
    s = s.replace("_", " ").replace("|", " ")
    s = re.sub(r"\s*@\s*", "\n", s)
    return re.sub(r"[ \t]+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default=r"D:\Games\SteamLibrary\steamapps\common\Legends of Idleon")
    ap.add_argument("--ru", default=os.path.join(ROOT, "..", "IdleOn-Rusificator", "translation"))
    a = ap.parse_args()
    njs, _pak = read_game(a.game)
    ru = {}
    if os.path.isdir(a.ru):
        for f in ("items.json", "lists.json", "code.json"):
            for k, v in json.load(open(os.path.join(a.ru, f), encoding="utf-8")).items():
                ru.setdefault(k, v)
    tr = lambda s: clean(ru[s]) if s in ru else None

    systems, src = [], []

    def system(en, ru_):
        key = (en, ru_)
        if key not in [(s["en"], s["ru"]) for s in systems]:
            systems.append({"en": en, "ru": ru_})
        return [(s["en"], s["ru"]) for s in systems].index(key)

    def add(si, name, texts, post=None):
        if name and "FILLER" in name.upper():
            return
        texts = [t.replace("{}", "{") for t in texts if is_text(t)]
        seen = set()
        for t in texts:
            if t in seen:
                continue
            seen.add(t)
            row = [si, clean(name) if name else "", tr(name) if name else "", clean(t), tr(t)]
            if post:
                row[3], row[4] = post(row[3]), post(row[4]) if row[4] else row[4]
            if row[3]:
                src.append(row)

    def ach(t):
        """Achievement rewards: '*STEAM_EXCLUSIVE_&*15_gems' -> only the lasting bonus lines."""
        t = re.sub(r"\{(?=\d)", "", t.replace("&", "\n").replace("*", ""))
        keep = [x.strip() for x in t.split("\n") if x.strip() and not re.search(r"STEAM|gems?$|самоцвет|time candy|конфет", x, re.I)]
        return re.sub(r"\s*\n\s*(?=[a-zа-я])", " ", "\n".join(keep))

    mobs = dict(re.findall(r'addNewMonster\("(\w+)",\{Name:"([^"]*)"', njs))

    # Talents: TalentDescriptions[i] = [[line1], [x1,x2,type...], [line2], [...]]; names from TalentIconNames
    names = re.search(r'TalentIconNames=function\(\)\{return"([^"]*)"', njs).group(1).split(" ")
    si = system("Talents", "Таланты")
    for i, r in enumerate(literal(njs, "TalentDescriptions")):
        n = names[i] if i < len(names) else ""
        if n in ("", "_", "BLAH") or n.startswith("FILLER"):
            continue
        add(si, n, [r[0][0], r[2][0]])
    # Alchemy: 4 bubble cauldrons, then vials
    alch = literal(njs, "AlchemyDescription")
    for c, (en, ru_) in enumerate([("Bubbles: Power (orange)", "Пузыри: сила (оранжевые)"),
                                   ("Bubbles: Quicc (green)", "Пузыри: ловкость (зелёные)"),
                                   ("Bubbles: High-IQ (purple)", "Пузыри: интеллект (фиолетовые)"),
                                   ("Bubbles: Kazam (yellow)", "Пузыри: казам (жёлтые)")]):
        si = system(en, ru_)
        for r in alch[c]:
            add(si, r[0], [r[9]])
    si = system("Alchemy vials", "Флаконы алхимии")
    for r in alch[4]:
        add(si, r[0], [r[9]])
    # Cards: CardStuff[world][i] = [mob id, code, ?, bonus text, value]
    si = system("Cards", "Карты")
    for grp in literal(njs, "CardStuff"):
        for r in grp:
            if isinstance(r, list) and len(r) > 3:
                n = mobs.get(r[0], r[0])
                src_n = len(src)
                add(si, n, [r[3]])
                for x in src[src_n:]:   # show the value per card level
                    x[3] = x[3].replace("{", str(r[4]))
                    x[4] = x[4].replace("{", str(r[4])) if x[4] else x[4]
    # Item definitions: stamps (desc_line1 is a CSV, text at [11]); gear unique stats; other desc lines
    it = itemdefs.parse(njs)
    si_st = system("Stamps", "Штампы")
    si_eq = system("Equipment, tools and obols", "Снаряжение, инструменты и оболы")
    si_it = system("Other items", "Прочие предметы")
    for k, d in it.items():
        dn = d.get("displayName", k)
        if d.get("Type") == "STAMP":
            f = str(d.get("desc_line1", "")).split(",")
            if len(f) > 11:
                add(si_st, dn, [f[11]])
            continue
        if d.get("kind") == "Equip":
            add(si_eq, dn, [str(d[u]) for u in ("UQ1txt", "UQ2txt") if str(d.get(u, "0")) not in ("0", "")])
            continue
        ls = [str(d.get("desc_line%d" % n, "")) for n in range(1, 9)]
        ls = [x for x in ls if re.search(r"[{}]", x)]
        if ls and d.get("Type") != "CARD":
            add(si_it, dn, ls)
    # Plain lists
    for lst, en, ru_, ni, ti in SOURCES:
        try:
            v = literal(njs, lst)
        except Exception as e:  # list renamed or removed in a game update
            print("skip", lst, e)
            continue
        si = system(en, ru_)
        for r in rows(v):
            if ti == "task":
                if len(r) > 1 and isinstance(r[0], str):
                    add(si, None, [r[0] + "_" + r[1]])
                continue
            n = r[ni] if ni is not None and ni < len(r) and isinstance(r[ni], str) else None
            if ti is None:
                ts = [x for x in r if x is not n]
            else:
                ts = [r[i] for i in ti if i < len(r)]
            add(si, n if n and LETTERS.search(n) else None, ts, ach if lst == "RegAchieves" else None)

    # Stats: match texts (EN) with the patterns of tools/stats.py
    cats = []
    for cat in CATEGORIES:
        out = {"en": cat["en"], "ru": cat["ru"], "stats": []}
        for st in cat["stats"]:
            inc = re.compile(st["re"], re.I)
            exc = re.compile(st["not"], re.I) if st.get("not") else None
            hits = [i for i, s in enumerate(src) if inc.search(s[3]) and not (exc and exc.search(s[3]))]
            out["stats"].append({"id": st["id"], "en": st["en"], "ru": st["ru"], "hits": hits})
        cats.append(out)

    # icon: the Power statue, cropped to its pixels (shown with integer scaling only)
    from gamecode import Assets
    im = Assets(njs, _pak).image("assets/data/EquipmentStatues1.png")
    im = im.crop(im.getbbox())
    os.makedirs(os.path.join(ROOT, "img"), exist_ok=True)
    im.save(os.path.join(ROOT, "img", "favicon.png"))
    print("img/favicon.png", im.size)

    acf = os.path.join(a.game, "..", "..", "appmanifest_1476970.acf")
    build = re.search(r'"buildid"\s+"(\d+)"', open(acf).read()).group(1) if os.path.exists(acf) else None
    data = {"build": build, "systems": systems, "src": src, "cats": cats}
    with open(os.path.join(ROOT, "src", "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    n_ru = sum(1 for s in src if s[4])
    print("src/data.json: %d sources in %d systems (%d with Russian text), %d stats, build %s"
          % (len(src), len(systems), n_ru, sum(len(c["stats"]) for c in cats), build))
    for c in cats:
        print(" ", c["en"], ", ".join("%s %d" % (s["id"], len(s["hits"])) for s in c["stats"]))


if __name__ == "__main__":
    main()
