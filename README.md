# Qur'an Translations Dataset  
### 96 Languages • 285 Translations • JSON Format

![GitHub stars](https://img.shields.io/github/stars/drmiaji/QuranTranslations)
![GitHub forks](https://img.shields.io/github/forks/drmiaji/QuranTranslations)
![License](https://img.shields.io/github/license/drmiaji/QuranTranslations)
![Repo size](https://img.shields.io/github/repo-size/drmiaji/QuranTranslations)

بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

A comprehensive open dataset providing **complete Qur'an translations in JSON format** covering **96 languages and 285 translation editions**.

This repository is intended for **developers, researchers, and Islamic applications** who need structured access to Qur'an translations.

All translations are provided as **full Qur'an JSON files**, accessible directly through **CDN links**, allowing easy integration into mobile apps, websites, and research tools.

GitHub Repository:  
https://github.com/drmiaji/QuranTranslations

---

## Features

- 🌍 **96 languages supported**  
- 📚 **285 translation editions**  
- 📄 **Full Qur'an translations**  
- 📝 **Footnotes supported**  
- ⚡ **CDN access via jsDelivr**  
- 📦 **Structured JSON format**  
- 🆓 **Open source**

---

## CDN Access (Recommended)

Translations can be accessed directly using **jsDelivr CDN**, which provides global caching and fast delivery.

### Base URL

https://cdn.jsdelivr.net/gh/drmiaji/QuranTranslations@latest/

---

## Example Translation Files

**English Translation**

https://cdn.jsdelivr.net/gh/drmiaji/QuranTranslations@latest/en/en_abdelhaleem.json

**Bengali Translation**

https://cdn.jsdelivr.net/gh/drmiaji/QuranTranslations@latest/bn/bn_mujibur.json

These files contain the **complete Qur'an translation**.

---

## Example Usage (JavaScript)

```javascript
fetch("https://cdn.jsdelivr.net/gh/drmiaji/QuranTranslations@latest/en/en_abdelhaleem.json")
  .then(response => response.json())
  .then(data => {
    console.log(data.suras[0].ayas[0].translation);
  });

---

Repository Structure

Translations are organized by language folders:

QuranTranslations
│
├── en
│   ├── en_abdelhaleem.json
│   ├── en_sahih.json
│   └── ...
│
├── bn
│   ├── bn_mujibur.json
│   └── ...
│
├── fr
│   └── ...
│
├── ar
│   └── ...
│
└── available_languages_info.json

Folder name → ISO language code

File name → specific translation edition

---

Translation Index

All supported languages and translations are listed in:

available_languages_info.json

CDN link:

https://cdn.jsdelivr.net/gh/drmiaji/QuranTranslations@latest/available_languages_info.json

This allows applications to discover available translations programmatically.

---

Data Structure

Each translation file contains the full Qur'an translation structured by surah and ayah:

{
  "suras": [
    {
      "index": "1",
      "ayas": [
        {
          "id": "1",
          "index": "1",
          "translation": "In the name of God, the Lord of Mercy, the Giver of Mercy",
          "footnotes": []
        }
      ]
    }
  ]
}

Field Description

Field	Description

suras	list of all Qur'an chapters
index	surah number
ayas	verses within the surah
id	unique verse identifier
translation	translated text
footnotes	optional translation notes

---

Supported Languages

This dataset currently includes 96 languages, including:

English, Arabic, Bengali, Urdu, French, German, Spanish, Russian, Turkish, Indonesian, Malay, Persian, Swahili, Tamil, Telugu, Chinese, Japanese, Korean, Vietnamese, and many more.

Full list available in:

available_languages_info.json

---

Use Cases

This dataset can be used for:

📱 Qur'an mobile applications

🌐 Islamic websites

📚 Qur'an study tools

🔍 NLP and linguistic research

📊 Translation comparison tools

🎓 Educational platforms

---
License

This project is licensed under:

GNU Affero General Public License v3.0

See the LICENSE file for full details.

Translations remain the intellectual property of their respective authors and publishers.

If you are a copyright holder and wish to request removal or modification, please open an issue.

---

Contributing

Contributions are welcome. You can help by:

Adding new translations

Fixing formatting issues

Improving metadata

Reporting issues

---

Support the Project

If this dataset is useful:

⭐ Star the repository

🔁 Share it with developers

🤝 Contribute improvements
