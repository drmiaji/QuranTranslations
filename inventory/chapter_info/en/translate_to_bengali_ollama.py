#!/usr/bin/env python3
"""
Translate 'text' field in Quran chapter_info JSON files to Bengali.
Uses Ollama (100% free, runs locally on your PC — no API key needed).

- Reads all JSON files from the input directory
- Translates only the 'text' field (preserving all HTML tags)
- Updates 'language_name' to 'bengali'
- Saves translated files to the bn\ output directory
- Skips already-translated files so you can safely resume if interrupted
"""

import json
import os
import ollama

# ── Configuration — no API key needed! ───────────────────────────────────────
INPUT_DIR  = r"C:\Apps\QuranTranslations\inventory\chapter_info\en"
OUTPUT_DIR = r"C:\Apps\QuranTranslations\inventory\chapter_info\bn"
MODEL      = "gemma3:4b"   # Free local model — already downloaded via: ollama pull gemma3:4b
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """You are a professional Islamic scholar and translator specializing in Quranic texts.
Translate the following HTML content from English to Bengali (বাংলা).

Rules:
1. Translate ONLY the human-readable text — do NOT translate or alter any HTML tags or attributes (e.g. <h2>, <p>, <strong>, <br> etc. must stay exactly as-is).
2. Preserve all HTML structure, whitespace, and newlines exactly.
3. Keep Arabic terms (e.g. surah names, hadith terminology, Allah, ﷺ) in their original Arabic script or transliteration — do not translate them.
4. Return ONLY the translated HTML string, with no explanation, preamble, or markdown code fences.

HTML content to translate:

{text}
"""


def translate_text(html_text: str) -> str:
    """Send HTML text to local Ollama model and return Bengali translation."""
    prompt = PROMPT_TEMPLATE.format(text=html_text)
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def process_files():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    json_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".json")])
    total = len(json_files)
    print(f"Found {total} JSON files in : {INPUT_DIR}")
    print(f"Output directory           : {OUTPUT_DIR}")
    print(f"Model                      : {MODEL} (local, free)\n")

    success_count = 0
    skip_count    = 0
    error_count   = 0

    for idx, filename in enumerate(json_files, start=1):
        output_path = os.path.join(OUTPUT_DIR, filename)

        # Resume support — skip files already translated
        if os.path.exists(output_path):
            print(f"[{idx:>3}/{total}] SKIP (exists) : {filename}")
            skip_count += 1
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        print(f"[{idx:>3}/{total}] Translating  : {filename} ...", end=" ", flush=True)

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            original_text = data["chapter_info"]["text"]

            translated_text = translate_text(original_text)

            # Update only the fields that should change
            data["chapter_info"]["text"]          = translated_text
            data["chapter_info"]["language_name"] = "bengali"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print("OK ✓")
            success_count += 1

        except KeyError as e:
            print(f"ERROR – missing key {e}")
            error_count += 1
        except Exception as e:
            print(f"ERROR – {e}")
            error_count += 1

    print(f"\n── Summary ────────────────────────────────")
    print(f"  Total files  : {total}")
    print(f"  Translated   : {success_count}")
    print(f"  Skipped      : {skip_count}")
    print(f"  Errors       : {error_count}")
    print(f"  Output dir   : {OUTPUT_DIR}")


if __name__ == "__main__":
    process_files()