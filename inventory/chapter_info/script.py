import os
import json
import openai  # pip install openai

# Set your OpenAI API key
openai.api_key = "YOUR_API_KEY"

# Paths
input_folder = r"D:\Quran_v4\QuranTranslations\inventory\chapter_info\en"
output_folder = r"D:\Quran_v4\QuranTranslations\inventory\chapter_info\bn_translated"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Function to translate text using OpenAI
def translate_to_bangla(text):
    prompt = f"Translate the following text into Bangla while keeping all HTML tags intact:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # fallback to original text

# Loop through all JSON files
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Translate relevant fields
            chapter_info = data.get("chapter_info", {})
            if "short_text" in chapter_info:
                chapter_info["short_text"] = translate_to_bangla(chapter_info["short_text"])
            if "text" in chapter_info:
                chapter_info["text"] = translate_to_bangla(chapter_info["text"])

            # Save to output folder
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Translated {filename} -> bn_translated")
        except Exception as e:
            print(f"Error processing {filename}: {e}")