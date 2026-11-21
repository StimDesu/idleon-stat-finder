"""The stat list of the finder, grouped by meaning.

Each stat has a regex (`re`, case-insensitive) matched against the English bonus text of every source, and
an optional `not` regex for texts that use the same words for something else (a monster's HP, a minigame's
damage...). Placeholders stay in the text: { and } are the number, so "+{% Drop Rate" matches "drop rate".
To add a stat: add a line, run `python tools/extract.py`, read the printed hit counts, open the page and
check the matches. Categories and stats keep their order on the page.
"""

MINIGAME = r"wraith|arcanist|depth charge|summoned units?|in competition|hounds?|cells?\b|jelly|tower defen|fireball|delve|tunnels?|minehead|sushi|bubba"


def S(id, en, ru, re, no=None):
    return {"id": id, "en": en, "ru": ru, "re": re, "not": no}


CATEGORIES = [
    {"en": "Character: attributes", "ru": "Персонаж: характеристики", "stats": [
        S("str", "STR", "Сила (STR)", r"\bSTR\b|\bstrength\b|all stats"),
        S("agi", "AGI", "Ловкость (AGI)", r"\bAGI\b|\bagility\b|all stats"),
        S("wis", "WIS", "Мудрость (WIS)", r"\bWIS\b|\bwisdom\b|all stats"),
        S("luk", "LUK", "Удача (LUK)", r"\bLUK\b|all stats"),
        S("hp", "Max HP", "Макс. здоровье (HP)", r"\bHP\b|\bhealth\b",
          r"monsters?|\bmobs?\b|enemy|enemies|units?\b|mental health|health food|boss(es)?\b(?! damage)|" + MINIGAME),
        S("mp", "Max MP", "Макс. мана (MP)", r"\bMP\b|\bmana\b", r"cost.{0,20}MP|" + MINIGAME),
    ]},
    {"en": "Character: combat", "ru": "Персонаж: бой", "stats": [
        S("dmg", "Damage", "Урон", r"\bdamage\b|\bDMG\b|weapon power",
          r"boss|crit|monsters? (deal|do)|take damage|damage taken|enemies|dodge|tempest form|in \w+ form|" + MINIGAME),
        S("wp", "Weapon power", "Сила оружия", r"weapon power|\bwep(on)? ?pow"),
        S("boss","Boss damage", "Урон по боссам", r"boss(es)? damage|damage (to(ward)?s?|against) (all )?bosses"),
        S("acc", "Accuracy", "Точность", r"accuracy", MINIGAME),
        S("def", "Defence", "Защита", r"defen[cs]e|\bDEF\b", MINIGAME),
        S("critc", "Critical chance", "Шанс крита", r"crit(ical)?( hit)? chance|chance to crit"),
        S("critd", "Critical damage", "Урон крита", r"crit(ical)? (hit )?damage|crit dmg"),
        S("move", "Movement speed", "Скорость передвижения", r"move(ment)? speed|walk speed"),
        S("multikill", "Multikill", "Мультикилл", r"multikill|multi-kill"),
        S("respawn", "Monster respawn", "Возрождение монстров", r"respawn"),
    ]},
    {"en": "Character: progress and loot", "ru": "Персонаж: прогресс и добыча", "stats": [
        S("classexp", "Class EXP", "Опыт класса", r"class (exp|xp)|(exp|xp) (from|when fight\w*) (all )?monsters|exp when fight"),
        S("drop", "Drop rate", "Шанс добычи (Drop rate)", r"drop rate|drop chance|\bDR\b|loot rate", r"card drop|stamps? drop"),
        S("coins", "Coins from monsters", "Монеты с монстров", r"coins? (from|dropped by) (all )?monsters|money from monsters|monster (cash|coins|money)|\bcash\b|\bcoins? gain", r"jade"),
        S("fightafk", "Fighting AFK gains", "AFK-доход в бою", r"fight(ing)? afk|afk gains? (for|of) all|all afk gains|afk gains rate"),
        S("talentpts", "Talent points", "Очки талантов", r"talent (points|pts)"),
        S("talentlv", "Talent levels", "Уровни талантов", r"lv for all talents|levels? (for|to) all talents|talent.{0,20}max lv|max lv.{0,30}talents?"),
        S("food", "Food effect", "Эффект еды", r"food effect|all food|health food|non-?consum|food .{0,10}not (be )?consumed"),
        S("cards", "Card drop", "Шанс выпадения карт", r"card drop|cards? drop"),
        S("crystal", "Crystal monsters", "Кристальные монстры", r"crystal (mob|monster)"),
        S("signs", "Star sign slots", "Слоты знаков зодиака", r"star signs?\b|infinite stars"),
    ]},
    {"en": "All skills", "ru": "Все навыки", "stats": [
        S("skillexp", "Skill EXP", "Опыт навыков", r"skill (exp|xp)|(exp|xp) (gain )?for all skills|all skill exp"),
        S("skilleff", "Skill efficiency", "Эффективность навыков", r"skill eff|efficiency for all skills|all skill eff"),
        S("skillafk", "Skill AFK gains", "AFK-доход навыков", r"skill(ing)? afk|afk gains? .{0,20}skills?"),
        S("carry", "Carry capacity", "Грузоподъёмность", r"carry(ing)? capacity|carry cap"),
    ]},
    {"en": "Gathering skills", "ru": "Навыки сбора", "stats": [
        S("mineff", "Mining efficiency", "Эффективность добычи руды", r"mining eff"),
        S("minexp", "Mining EXP", "Опыт добычи руды", r"mining (exp|xp)"),
        S("multiore", "Multi-ore", "Мульти-руда", r"multi-?ore"),
        S("chopeff", "Choppin efficiency", "Эффективность рубки", r"choppin'?g?\s*eff"),
        S("chopexp", "Choppin EXP", "Опыт рубки", r"choppin'?g? (exp|xp)"),
        S("multilog", "Multi-log", "Мульти-бревно", r"multi-?log"),
        S("fisheff", "Fishing efficiency", "Эффективность рыбалки", r"fishing eff"),
        S("fishexp", "Fishing EXP", "Опыт рыбалки", r"fishing (exp|xp)"),
        S("catcheff", "Catching efficiency (bugs)", "Эффективность ловли насекомых", r"catching eff|bug catching"),
        S("catchexp", "Catching EXP", "Опыт ловли насекомых", r"catching (exp|xp)"),
        S("trapeff", "Trapping efficiency", "Эффективность ловушек", r"trapping eff|critters?|trap(ping)? (box|speed)"),
        S("trapexp", "Trapping EXP", "Опыт ловушек", r"trapping (exp|xp)"),
        S("worship", "Worship (charge, souls)", "Поклонение (заряд, души)", r"worship|charge rate|max charge|\bsouls?\b"),
    ]},
    {"en": "Production skills", "ru": "Навыки производства", "stats": [
        S("anvil", "Anvil / smithing", "Наковальня / кузнечное дело", r"anvil|smithing"),
        S("brew", "Alchemy: brew speed", "Алхимия: скорость варки", r"brew speed|cauldron"),
        S("liquid", "Alchemy: liquids", "Алхимия: жидкости", r"liquid|water (gain|rate|regen)"),
        S("bubblecost", "Bubble and vial costs", "Цена пузырей и флаконов", r"bubble (upgrade )?costs?|vial (upgrade )?costs?|cheaper bubbles?|bubbles? cost"),
        S("build", "Construction build rate", "Скорость стройки", r"build (rate|speed)|construction (exp|speed)|flaggy|\bcogs?\b"),
        S("refinery", "Refinery and 3D printer", "Очистительный завод и 3D-принтер", r"refinery|printer|sample"),
        S("stampcost", "Stamp costs", "Цена штампов", r"stamps?.{0,20}(cost|cheaper|less)|(cost|cheaper).{0,20}stamps?"),
    ]},
    {"en": "Cooking", "ru": "Кулинария", "stats": [
        S("cookspd", "Meal cooking speed", "Скорость готовки блюд", r"(meal )?cooking speed|meal (cook\w* )?spd|meal speed|cook(ing)? meals? .{0,10}faster|meal cooking"),
        S("recipe", "New recipe speed (fire)", "Скорость новых рецептов (огонь)", r"new recipe|recipe (speed|cooking)|recipe cook"),
        S("mealbonus", "Meal bonuses", "Бонусы блюд", r"bonuses (from|of) (all )?meals|meal bonus|all meal"),
        S("kitchen", "Kitchen costs and upgrades", "Цена кухонь и улучшений", r"kitchen"),
        S("cookexp", "Cooking EXP", "Опыт кулинарии", r"cooking (exp|xp)"),
    ]},
    {"en": "Breeding and lab", "ru": "Разведение и лаборатория", "stats": [
        S("breed", "Breeding (eggs, pets, genes)", "Разведение (яйца, питомцы, гены)", r"breeding|\beggs?\b|pet (power|dmg|damage)|genes?\b|shiny"),
        S("linewidth", "Lab line width and range", "Ширина линии и дальность в лаборатории", r"line width|connection range|lab range", r"no matter what|outposts?|guard"),
        S("labexp", "Lab EXP", "Опыт лаборатории", r"lab(oratory)? (exp|xp)"),
    ]},
    {"en": "Later worlds", "ru": "Поздние миры", "stats": [
        S("sailing", "Sailing (boat speed, loot)", "Плавание (скорость лодок, добыча)", r"boat speed|loot value|sailing|artifact find|captain"),
        S("divinity", "Divinity points", "Очки божественности", r"divinity"),
        S("gaming", "Gaming (bits, sprouts)", "Игры (биты, ростки)", r"\bbits?\b|gaming|sprouts?|₣"),
        S("farming", "Farming (crops, evolution)", "Фермерство (урожай, эволюция)", r"\bcrops?\b|crop evo|evolution|\bOG\b|farming|plants?\b"),
        S("sneaking", "Sneaking (stealth, jade)", "Скрытность (скрытность, нефрит)", r"stealth|\bjade\b|sneaking|ninja"),
        S("summoning", "Summoning (essence)", "Призыв (эссенция)", r"essence|summoning"),
        S("spelunk", "Spelunking (POW, amber)", "Спелеология (POW, янтарь)", r"\bPOW\b|spelunk|amber"),
        S("research", "Research", "Исследования", r"research (exp|pts|points)"),
        S("caverns", "Caverns (W5 villagers)", "Пещеры (жители 5-го мира)", r"villagers?|opals?|caverns?|bucket"),
        S("dungeon", "Dungeons", "Подземелья", r"dungeon|flurbo"),
    ]},
]
