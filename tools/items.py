"""Reads every item definition (`X.addNewEquip/Item/Consumable/Quest("Id", e)`) from N.js.
Each definition is a run of `.h.key=value` assignments right before its addNew call."""
import json, re, sys

CALL = re.compile(r'\.addNew(Equip|Item|Consumable|Quest)\("([^"]+)",\w+\)')
FIELD = re.compile(r'\.h\.(\w+)=("(?:[^"\\]|\\.)*"|-?[\d.]+(?:e[-+]?\d+)?)')


def parse(src):
    items, prev = {}, 0
    for m in CALL.finditer(src):
        seg = src[prev:m.start()]
        prev = m.end()
        # a definition starts at its displayName; skip earlier noise (function headers etc.)
        k = seg.rfind('.h.displayName=')
        if k < 0:
            continue
        d = {"kind": m.group(1)}
        for f in FIELD.finditer(seg, k):
            v = f.group(2)
            d.setdefault(f.group(1), json.loads(v) if v[0] == '"' else float(v) if "." in v or "e" in v else int(v))
        items[m.group(2)] = d
    return items


if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read()
    items = parse(src)
    json.dump(items, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
    print(len(items), "items")
