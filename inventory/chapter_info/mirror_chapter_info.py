import json
import os
import time
import requests

BASE = "https://api.quran.com/api/v4/chapters/{chapter}/info?language={lang}"

# choose languages you want to mirror
LANGS = ["en", "ur", "bn"]  # add more: "fr", "id", etc.
CHAPTERS = range(1, 115)

OUT_DIR = "chapter_info_mirror"   # you can commit this into a repo
os.makedirs(OUT_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Quran_v4 chapter info mirrorer"})

for lang in LANGS:
    lang_dir = os.path.join(OUT_DIR, lang)
    os.makedirs(lang_dir, exist_ok=True)

    for chapter in CHAPTERS:
        url = BASE.format(chapter=chapter, lang=lang)
        r = session.get(url, timeout=60)
        r.raise_for_status()

        # Save EXACT JSON (structure intact)
        data = r.json()

        # Optional sanity check: ensure expected keys exist
        if "chapter_info" not in data or "text" not in data["chapter_info"]:
            raise RuntimeError(f"Unexpected structure for {url}")

        out_path = os.path.join(lang_dir, f"{chapter}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        print("saved", out_path)
        time.sleep(0.2)  # be polite to the API