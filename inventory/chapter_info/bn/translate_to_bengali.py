"""
Batch JSON Translator — English text field → Bengali
Usage:
  1. pip install anthropic
  2. Set your API key: export ANTHROPIC_API_KEY="sk-ant-..."
  3. python translate_to_bengali.py --input ./your_json_folder --output ./translated
"""

import os
import json
import time
import argparse
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def translate_html_to_bengali(html_text: str) -> str:
    """Send the HTML text to Claude and get Bengali translation back."""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": (
                    "Translate the following HTML content from English to Bengali. "
                    "Keep all HTML tags, attributes, href links, and structure exactly as-is. "
                    "Only translate the visible text content between the tags. "
                    "Do not add any explanation or commentary — return ONLY the translated HTML.\n\n"
                    + html_text
                ),
            }
        ],
    )
    return message.content[0].text.strip()


def translate_file(input_path: Path, output_path: Path) -> bool:
    """Translate a single JSON file. Returns True on success."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        original_text = data.get("chapter_info", {}).get("text")
        if not original_text:
            print(f"  [SKIP] No 'text' field found in chapter_info: {input_path.name}")
            return False

        translated = translate_html_to_bengali(original_text)
        data["chapter_info"]["text"] = translated

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"  [ERROR] {input_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Batch translate JSON text fields to Bengali")
    parser.add_argument("--input",  default=r"D:\Quran_v4\QuranTranslations\inventory\chapter_info\bn", help="Folder containing your JSON files")
    parser.add_argument("--output", default="./translated", help="Folder to save translated files")
    parser.add_argument("--delay",  type=float, default=0.5, help="Seconds to wait between API calls (default 0.5)")
    args = parser.parse_args()

    input_dir  = Path(args.input)
    output_dir = Path(args.output)
    json_files = sorted(input_dir.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in: {input_dir.resolve()}")
        return

    print(f"Found {len(json_files)} JSON file(s) in '{input_dir}'")
    print(f"Translated files will be saved to '{output_dir}'\n")

    done, skipped, errors = 0, 0, 0

    for i, src in enumerate(json_files, 1):
        dst = output_dir / src.name
        print(f"[{i}/{len(json_files)}] {src.name} ...", end=" ", flush=True)

        success = translate_file(src, dst)
        if success:
            done += 1
            print("✓ done")
        else:
            errors += 1

        if i < len(json_files):
            time.sleep(args.delay)

    print(f"\n{'='*50}")
    print(f"Translated : {done}")
    print(f"Errors     : {errors}")
    print(f"Output dir : {output_dir.resolve()}")


if __name__ == "__main__":
    main()