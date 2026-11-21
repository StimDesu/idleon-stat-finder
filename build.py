"""Builds index.html from src/template.html and src/data.json (made by tools/extract.py)."""
import json, pathlib
root = pathlib.Path(__file__).parent
data = json.loads((root / "src/data.json").read_text(encoding="utf-8"))
t = (root / "src/template.html").read_text(encoding="utf-8")
out = t.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
(root / "index.html").write_text(out, encoding="utf-8")
print(f"index.html: {len(data['src'])} bonus texts, {sum(len(c['stats']) for c in data['cats'])} stats, game build {data['build']}")
