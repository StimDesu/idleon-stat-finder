"""Helpers for reading the game's N.js: the code file, list literals and the asset pack."""
import gzip, io, json, os, re

import asar, pak


def read_game(game):
    """N.js text and default.pak bytes. The untouched app.asar.ru-backup wins if the Rusificator is installed."""
    res = os.path.join(game, "resources")
    path = os.path.join(res, "app.asar.ru-backup")
    if not os.path.exists(path):
        path = os.path.join(res, "app.asar")
    header, base = asar.read_header(path)
    want = {"distBuild/static/game/N.js": None, "distBuild/static/game/lib/default.pak": None}
    with open(path, "rb") as f:
        for p, e in asar.walk(header):
            if p in want:
                f.seek(base + int(e["offset"]))
                want[p] = f.read(e["size"])
    print("read", path)
    return want["distBuild/static/game/N.js"].decode("utf-8"), want["distBuild/static/game/lib/default.pak"]


def _split(mm):
    s, sep = json.loads(mm.group(1)), json.loads(mm.group(2))
    return json.dumps(s.split(sep) if sep else list(s))


def literal(src, name):
    """Value of `X.<name>=function(){return <literal>}`; `"a b".split(" ")` is expanded."""
    m = re.search(r"\." + name + r"=function\(\)\{return", src)
    i, depth, q, start = m.end(), 0, None, m.end()
    while True:
        c = src[i]
        if q:
            if c == "\\":
                i += 1
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                break
            depth -= 1
        i += 1
    body = re.sub(r'("(?:[^"\\]|\\.)*")\.split\(("(?:[^"\\]|\\.)*")\)', _split, src[start:i])
    return json.loads(body)


class Assets:
    """PNG images from default.pak by asset id (e.g. 'assets/data/CookingSpice0.png')."""

    def __init__(self, njs, pakdata):
        self.pak = pakdata
        self.ent = {e["id"]: e for e in pak.HaxeUnserializer(pak.MANIFEST_RE.search(njs).group(1)).read() if "position" in e}

    def ids(self, pattern):
        return sorted(k for k in self.ent if re.search(pattern, k))

    def image(self, aid):
        from PIL import Image
        e = self.ent[aid]
        raw = self.pak[e["position"]:e["position"] + e["length"]]
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
        return Image.open(io.BytesIO(raw)).convert("RGBA")
