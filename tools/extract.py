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
def custom_map(njs, name):
    """CustomMaps.<name>: `Ma.<name>=function(){var e=new l;return e.h[0]="...",...,e}` -> list by id."""
    m = re.search(r"\." + name + r"=function\(\)\{var e=new l;return (.*?),e\}", njs)
    d = {int(k): v for k, v in re.findall(r'e\.h\[(\d+)\]="([^"]*)"', m.group(1))}
    return [d.get(i, "") for i in range(max(d) + 1)]


def star_sign_table(njs):
    """v.StarSigns() adds fixed numbers per equipped sign: `if(D.contains(StarSignsDL,"14")){...=5+N(StarSigns.h.Drop)...}`.
    Returns {sign index: [[key, value], ...]}."""
    i = njs.find("._customBlock_StarSigns=function")
    body = njs[i:i + 60000]
    marks = [(m.start(), m.group(1)) for m in re.finditer(r'D\.contains\([^,]*StarSignsDL,"(\d+)"\)', body)]
    out = {}
    for n, (pos, sid) in enumerate(marks):
        seg = body[pos:marks[n + 1][0] if n + 1 < len(marks) else pos + 3000]
        pairs = re.findall(r'(-?\d+(?:\.\d+)?)\+c\.asNumber\(a\.engine\.getGameAttribute\("DNSM"\)\.h\.StarSigns\.h\.(\w+)\)', seg)
        if pairs:
            out.setdefault(int(sid), [])
            for v, k in pairs:
                if [k, fnum(v)] not in out[int(sid)]:
                    out[int(sid)].append([k, fnum(v)])
    return out


def game_model(njs, it):
    """Tables the page needs to rebuild the game's own bonus maps (TotalStats, AlchBubbles, StampBonusOfTypeX...)."""
    L = lambda n: literal(njs, n)
    alch = L("AlchemyDescription")
    cards = {}
    for grp in L("CardStuff"):
        for r in grp:
            if isinstance(r, list) and len(r) > 4:
                cards[r[0]] = [r[3], fnum(r[4]), fnum(r[2])]
    gear = {}
    for k, d in it.items():
        if d.get("kind") == "Equip":
            gear[k] = {f: d[f] for f in ("STR", "AGI", "WIS", "LUK", "Defence", "Weapon_Power", "Speed",
                                          "UQ1txt", "UQ1val", "UQ2txt", "UQ2val") if d.get(f) not in (None, 0, "0", "")}
    stamps = [[str(it.get("Stamp%s%d" % (c, n), {}).get("desc_line1", "")) for n in range(1, 200)
               if "Stamp%s%d" % (c, n) in it] for c in "ABC"]
    return {
        "tal": [[fnum(r[1][0]), fnum(r[1][1]), r[1][2], fnum(r[1][3]), fnum(r[1][4]), r[1][5]] for r in L("TalentDescriptions")],
        "bub": [[[r[3], fnum(r[1]), fnum(r[2]), r[15]] for r in alch[c]] for c in range(4)],
        "vial": [[r[3], fnum(r[1]), fnum(r[2]), r[11] if len(r) > 11 else ""] for r in alch[4]],
        "stamps": stamps,
        "signs": star_sign_table(njs),
        "cards": cards,
        "idCard": custom_map(njs, "IDforCardBonus"), "idEtc": custom_map(njs, "IDforETCbonus"),
        "idCardSet": custom_map(njs, "IDforCardSETbonus"),
        "fam": [[fnum(r[1]), fnum(r[2]), r[3], fnum(r[4]), fnum(r[5]), r[6]] for r in L("ClassFamilyBonuses")],
        "famLv": [fnum(r[1]) for r in L("ClassAccountBonus")],
        "guild": [[r[6], fnum(r[4]), fnum(r[5])] for r in L("GuildBonuses")],
        "prayer": [[fnum(r[3]), fnum(r[4])] for r in L("PrayerInfo")],
        "shrine": [[fnum(r[2]), fnum(r[3])] for r in L("ShrineInfo")],
        "sigil": [[fnum(r[3]), fnum(r[4]), fnum(r[8]), fnum(r[10]), fnum(r[12])] for r in L("SigilDesc")],
        "arcade": [[r[3], fnum(r[1]), fnum(r[2])] for r in L("ArcadeShopInfo")],
        "vault": [fnum(r[5]) for r in L("UpgradeVault")],
        "grim": [fnum(r[5]) for r in L("GrimoireUpg")],
        "chip": [[r[10], fnum(r[11])] for r in L("ChipDesc")],
        "comp": [[fnum(r[2]), fnum(r[11]) if len(r) > 11 else 0] for r in L("CompanionDB")],
        # Pristine charms: CustomMaps NjEQ "NjTrP<t>" = "... ... ... <bonus>" (PristineBon(t) when Ninja[107][t] == 1)
        "pristine": {int(t): fnum(v.split(" ")[3]) for t, v in re.findall(r'NjTrP(\d+)="([^"]+)"', njs) if len(v.split(" ")) > 3},
        "meals": [[fnum(r[2]), r[5]] for r in L("MealINFO")],
        "statue": [fnum(r[3]) for r in L("StatueInfo")],
        "salt": [fnum(r[3]) for r in L("SaltLicks")],
        "gear": gear,
    }


def fnum(s):
    try:
        f = float(s)
    except (TypeError, ValueError):
        return 0
    return int(f) if f.is_integer() and abs(f) < 1e15 else f


# How the page reads a row's current value from the save: list -> (row index, row) -> calc spec.
# Each spec is interpreted by value() in src/template.html; the formulas are the game's base values
# (most systems have extra account multipliers on top, which are not counted - see the page notes).
CALC = {
    "StatueInfo": lambda i, r: ["statue", i, fnum(r[3])],                 # StatueLevels_N[i][0] * [3], x2 onyx
    "StarSigns": lambda i, r: ["sign", i],                               # equipped in PVtStarSign_N; number is in the text
    "ShrineInfo": lambda i, r: ["shrine", i, fnum(r[2]), fnum(r[3])],    # (lv-1)*[3] + [2]
    "GuildBonuses": lambda i, r: ["guild", i, r[6], fnum(r[4]), fnum(r[5])],   # f5([6],[4],[5],Guild[0][i])
    "BribeDescriptions": lambda i, r: ["bribe", i, fnum(r[5])],          # BribeStatus[i] == 1
    "ArcadeShopInfo": lambda i, r: ["arc", i, r[3], fnum(r[1]), fnum(r[2])],
    "RegAchieves": lambda i, r: ["ach", i],                              # AchieveReg[i] == -1
    "PrayerInfo": lambda i, r: ["prayer", i, fnum(r[3])],                # round([3] * max(1, 1+(lv-1)/10)) if equipped
    "UpgradeVault": lambda i, r: ["lv", "UpgVault", i, fnum(r[5])],
    "AtomInfo": lambda i, r: ["lv", "Atoms", i, fnum(r[4])],
    "GrimoireUpg": lambda i, r: ["lv", "Grimoire", i, fnum(r[5])],
    "ArcaneUpg": lambda i, r: ["lv", "Arcane", i, fnum(r[5])],
    "CompassUpg": lambda i, r: ["lv", "Compass.0", i, fnum(r[5])],
    "MealINFO": lambda i, r: ["lv", "Meals.0", i, fnum(r[2])],
    "SigilDesc": lambda i, r: ["sigil", i, [fnum(r[3]), fnum(r[4]), fnum(r[8]), fnum(r[10]), fnum(r[12])]],
    "ChipDesc": lambda i, r: ["chip", i, fnum(r[11])],                    # chip i in Lab[1+n]
    "JewelDesc": lambda i, r: ["jewel", i, fnum(r[12])],                  # Lab[14][i] == 1
}

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

    systems, src, seen_rows = [], [], set()

    def system(en, ru_):
        key = (en, ru_)
        if key not in [(s["en"], s["ru"]) for s in systems]:
            systems.append({"en": en, "ru": ru_})
        return [(s["en"], s["ru"]) for s in systems].index(key)

    def add(si, name, texts, post=None, calc=None, join=False):
        """One row per bonus text: [system, name EN, name RU, text EN, text RU, calc].
        calc tells the page how to read the current value from a save (see `value()` in src/template.html).
        join=True puts all texts of the source in one row (talents: long and short description of one number)."""
        if name and "FILLER" in name.upper():
            return
        texts = [t.replace("{}", "{") for t in texts if is_text(t)]
        if join and len(texts) > 1:
            en_ = "\n".join(clean(t) for t in texts)
            ru_ = "\n".join(tr(t) or clean(t) for t in texts) if any(tr(t) for t in texts) else None
            key = (si, clean(name) if name else "", en_)
            if key not in seen_rows:
                seen_rows.add(key)
                src.append([si, clean(name) if name else "", tr(name) if name else "", en_, ru_, calc])
            return
        seen = set()
        for t in texts:
            if t in seen:
                continue
            seen.add(t)
            row = [si, clean(name) if name else "", tr(name) if name else "", clean(t), tr(t), calc]
            if post:
                row[3], row[4] = post(row[3]), post(row[4]) if row[4] else row[4]
            key = (si, row[1], row[3])
            if row[3] and key not in seen_rows:   # some lists repeat a row (e.g. achievements for two platforms)
                seen_rows.add(key)
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
        p = r[1]   # GetTalentNumber(1,t): f5(p[2], p[0], p[1], lv); GetTalentNumber(2,t): p[3..5]
        add(si, n, [r[0][0], r[2][0]], calc=["tal", i, p[2], fnum(p[0]), fnum(p[1]), p[5], fnum(p[3]), fnum(p[4])], join=True)
    # Alchemy: 4 bubble cauldrons, then vials. Value f5([3], [1], [2], CauldronInfo[c][i]); key [15]
    alch = literal(njs, "AlchemyDescription")
    for c, (en, ru_) in enumerate([("Bubbles: Power (orange)", "Пузыри: сила (оранжевые)"),
                                   ("Bubbles: Quicc (green)", "Пузыри: ловкость (зелёные)"),
                                   ("Bubbles: High-IQ (purple)", "Пузыри: интеллект (фиолетовые)"),
                                   ("Bubbles: Kazam (yellow)", "Пузыри: казам (жёлтые)")]):
        si = system(en, ru_)
        for i, r in enumerate(alch[c]):
            add(si, r[0], [r[9]], calc=["bub", c, i, r[3], fnum(r[1]), fnum(r[2]), 1 if "ACTIVE" in str(r[15]) else 0])
    si = system("Alchemy vials", "Флаконы алхимии")
    for i, r in enumerate(alch[4]):
        add(si, r[0], [r[9]], calc=["vial", i, r[3], fnum(r[1]), fnum(r[2])])
    # Cards: CardStuff[world][i] = [mob id, code, ?, bonus text, value]
    si = system("Cards", "Карты")
    for grp in literal(njs, "CardStuff"):
        for r in grp:
            if isinstance(r, list) and len(r) > 3:
                n = mobs.get(r[0], r[0])
                add(si, n, [r[3]], calc=["card", r[0], fnum(r[2]), fnum(r[4])])   # value = [4] per card level
    # Item definitions: stamps (desc_line1 is a CSV, text at [11]); gear unique stats; other desc lines
    it = itemdefs.parse(njs)
    si_st = system("Stamps", "Штампы")
    si_eq = system("Equipment, tools and obols", "Снаряжение, инструменты и оболы")
    si_it = system("Other items", "Прочие предметы")
    for k, d in it.items():
        dn = d.get("displayName", k)
        if d.get("Type") == "STAMP":
            f = str(d.get("desc_line1", "")).split(",")
            m = re.match(r"Stamp([ABC])(\d+)$", k)
            if len(f) > 11 and m:   # StampLv[cat][n-1]; value f5(f[1], f[2], f[3], lv)
                add(si_st, dn, [f[11]], calc=["stamp", "ABC".index(m.group(1)), int(m.group(2)) - 1, f[1], fnum(f[2]), fnum(f[3])])
            continue
        if d.get("kind") == "Equip":
            for u in ("1", "2"):
                t = str(d.get("UQ%stxt" % u, "0"))
                if t not in ("0", ""):   # gear unique stat: base UQval + stone upgrades (EMm*_N[slot].UQval)
                    add(si_eq, dn, [t], calc=["gear", k, int(u), fnum(d.get("UQ%sval" % u, 0))])
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
        # rows of a flat list keep their index (the save keeps levels by the same index)
        flat = all(isinstance(r, list) and any(isinstance(x, str) for x in r) for r in v)
        index = {id(r): i for i, r in enumerate(v)} if flat else {}
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
            calc = None
            if lst in CALC and id(r) in index:
                try:
                    calc = CALC[lst](index[id(r)], r)
                except (ValueError, IndexError):
                    calc = None
            add(si, n if n and LETTERS.search(n) else None, ts, ach if lst == "RegAchieves" else None, calc)
    # Base stats of equipped gear, tools and obols: one row per stat
    for f, t in (("STR", "+{_STR"), ("AGI", "+{_AGI"), ("WIS", "+{_WIS"), ("LUK", "+{_LUK"),
                 ("Defence", "+{_Defence"), ("Weapon_Power", "+{_Weapon_Power")):
        add(si_eq, "Equipped_gear,_tools_and_obols", [t], calc=["gearstat", f])
        src[-1][2] = "Надетое снаряжение, инструменты и оболы"   # a row of this page, not a game text

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
    # base stats of every wearable (for the "Equipped gear" rows): key -> [STR, AGI, WIS, LUK, Defence, Weapon_Power]
    gear = {k: [fnum(d.get(f, 0)) for f in ("STR", "AGI", "WIS", "LUK", "Defence", "Weapon_Power")]
            for k, d in it.items() if d.get("kind") == "Equip"}
    gear = {k: v for k, v in gear.items() if any(v)}
    g = game_model(njs, it)
    # Number2Letter (save flags such as super bits and exalted stamps use it): game.mbs list + TournyStuff
    import gzip
    e = Assets(njs, _pak).ent["assets/data/game.mbs"]
    raw = _pak[e["position"]:e["position"] + e["length"]]
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    j = raw.find(b"Number2Letter")
    m = re.search(rb"(?:\x00\x00\x00\x01(.))+", raw[j:j + 2000])
    g["n2l"] = [c.decode() for c in re.findall(rb"\x00\x00\x00\x01(.)", m.group(0))] + [x for row in literal(njs, "TournyStuff") for x in row]
    print("game model: %d talents, %d star signs, %d cards, %d stamps" % (len(g["tal"]), len(g["signs"]), len(g["cards"]), sum(map(len, g["stamps"]))))
    data = {"build": build, "systems": systems, "src": src, "cats": cats, "gear": gear, "g": g}
    with open(os.path.join(ROOT, "src", "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    n_ru = sum(1 for s in src if s[4])
    print("src/data.json: %d sources in %d systems (%d with Russian text), %d stats, build %s"
          % (len(src), len(systems), n_ru, sum(len(c["stats"]) for c in cats), build))
    for c in cats:
        print(" ", c["en"], ", ".join("%s %d" % (s["id"], len(s["hits"])) for s in c["stats"]))


if __name__ == "__main__":
    main()
