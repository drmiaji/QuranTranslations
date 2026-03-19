#!/usr/bin/env python3
"""
Download tafsirs from Quran.com API in the EXACT structure used by the app
Structure: tafsirKey/chapter_N/verse_M.json
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
API_BASE_URL = "https://api.quran.com/api/v4"
OUTPUT_DIR = Path("./tafsir_data")  # Will be: tafsirKey/chapter_N/verse_M.json
TOTAL_CHAPTERS = 114
MAX_WORKERS = 5
REQUEST_TIMEOUT = 10

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_tafsirs_list() -> Optional[List[Dict]]:
    """Fetch list of available tafsirs from Quran.com"""
    try:
        print("📥 Fetching tafsirs list from Quran.com API...")
        url = f"{API_BASE_URL}/resources/tafsirs"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        tafsirs = data.get('tafsirs', [])
        print(f"✅ Found {len(tafsirs)} tafsirs available\n")
        
        for tafsir in tafsirs:
            print(f"  📖 {tafsir.get('name')} (ID: {tafsir.get('id')}, Slug: {tafsir.get('slug')})")
        
        return tafsirs
    except Exception as e:
        print(f"❌ Error fetching tafsirs: {e}")
        return None

def get_tafsir_data(tafsir_id: int, chapter: int, verse: int) -> Optional[Dict]:
    """Fetch tafsir data for a specific verse from Quran.com"""
    try:
        # Quran.com uses tafsir ID (not slug) for API calls
        verse_key = f"{chapter}:{verse}"
        url = f"{API_BASE_URL}/quran/{verse_key}/tafsirs/{tafsir_id}"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 404:
            return None  # Tafsir not available for this verse
        
        response.raise_for_status()
        data = response.json()
        
        # Extract tafsir text from response
        if 'tafsir' in data:
            tafsir = data['tafsir']
            if isinstance(tafsir, dict):
                return tafsir
            elif isinstance(tafsir, list) and len(tafsir) > 0:
                return tafsir[0]
        
        return None
    except Exception as e:
        return None

def save_tafsir_verse(tafsir_key: str, chapter: int, verse: int, data: Dict) -> bool:
    """Save tafsir in exact app structure: tafsirKey/chapter_N/verse_M.json"""
    try:
        # Exact structure: tafsirKey/chapter_N/verse_M.json
        tafsir_dir = OUTPUT_DIR / tafsir_key / f"chapter_{chapter}"
        tafsir_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = tafsir_dir / f"verse_{verse}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return False

def download_single_verse(args: tuple) -> tuple:
    """Download a single verse (for parallel processing)"""
    tafsir_id, tafsir_key, chapter, verse = args
    
    data = get_tafsir_data(tafsir_id, chapter, verse)
    
    if data is None:
        return (tafsir_key, chapter, verse, False, 0)
    
    # Check if tafsir has text
    if data.get('text') and len(str(data.get('text', '')).strip()) > 0:
        success = save_tafsir_verse(tafsir_key, chapter, verse, data)
        return (tafsir_key, chapter, verse, success, 1 if success else 0)
    
    return (tafsir_key, chapter, verse, False, 0)

def download_tafsir_parallel(tafsir_id: int, tafsir_key: str, tafsir_name: str) -> int:
    """Download all verses for a tafsir using parallel downloads"""
    
    print(f"\n📖 Downloading: {tafsir_name}")
    print(f"   Key: {tafsir_key} | ID: {tafsir_id}")
    print(f"   Using {MAX_WORKERS} parallel workers...\n")
    
    # Create list of all (chapter, verse) pairs
    download_tasks = []
    for chapter in range(1, TOTAL_CHAPTERS + 1):
        for verse in range(1, 300):  # Max verses
            download_tasks.append((tafsir_id, tafsir_key, chapter, verse))
    
    total_downloaded = 0
    chapters_with_verses = set()
    completed_tasks = 0
    
    # Parallel download
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(download_single_verse, task): task 
            for task in download_tasks
        }
        
        for future in as_completed(futures):
            completed_tasks += 1
            
            try:
                tafsir_key_result, chapter, verse, success, count = future.result()
                
                if success:
                    total_downloaded += count
                    chapters_with_verses.add(chapter)
                
                # Progress update
                if completed_tasks % 1000 == 0:
                    progress = (completed_tasks / len(download_tasks)) * 100
                    print(f"   [{progress:5.1f}%] {total_downloaded:6d} verses downloaded", end='\r')
                    
            except Exception as e:
                pass
    
    chapters_with_content = len(chapters_with_verses)
    print(f"   ✅ Downloaded: {total_downloaded:6d} verses in {chapters_with_content:3d} chapters" + " " * 30)
    
    return total_downloaded

def download_all_tafsirs():
    """Download all available tafsirs"""
    
    tafsirs = get_tafsirs_list()
    if not tafsirs:
        print("❌ Failed to fetch tafsirs")
        return
    
    print("=" * 70)
    print(f"🎯 Starting PARALLEL download of {len(tafsirs)} tafsirs")
    print(f"📁 Structure: {{tafsirKey}}/chapter_{{N}}/verse_{{M}}.json")
    print(f"⚡ Workers: {MAX_WORKERS}")
    print("=" * 70)
    
    start_time = time.time()
    total_verses_all = 0
    successful_tafsirs = 0
    failed_tafsirs = 0
    
    for idx, tafsir in enumerate(tafsirs, 1):
        tafsir_id = tafsir.get('id')
        tafsir_slug = tafsir.get('slug')
        tafsir_name = tafsir.get('name', tafsir_slug)
        tafsir_lang = tafsir.get('language_name', 'Unknown')
        
        if not tafsir_id:
            print(f"⚠️  Skipping (no ID): {tafsir_name}")
            continue
        
        # Use slug as the key (matches app structure)
        tafsir_key = tafsir_slug
        
        print(f"\n[{idx}/{len(tafsirs)}] {tafsir_name} ({tafsir_lang})")
        
        try:
            downloaded = download_tafsir_parallel(tafsir_id, tafsir_key, tafsir_name)
            
            if downloaded > 0:
                total_verses_all += downloaded
                successful_tafsirs += 1
            else:
                print(f"   ⚠️  No verses downloaded")
                failed_tafsirs += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_tafsirs += 1
    
    elapsed_time = time.time() - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    
    print("\n" + "=" * 70)
    print("📊 DOWNLOAD COMPLETE")
    print("=" * 70)
    print(f"✅ Successful: {successful_tafsirs}/{len(tafsirs)}")
    print(f"❌ Failed: {failed_tafsirs}/{len(tafsirs)}")
    print(f"📝 Total verses: {total_verses_all:,}")
    print(f"⏱️  Time taken: {hours}h {minutes}m")
    print(f"📁 Output: {OUTPUT_DIR.absolute()}")
    print("\nStructure:")
    print(f"  {OUTPUT_DIR}/")
    print(f"  ├── en-tafsir-ibn-kathir/")
    print(f"  │   ├── chapter_1/")
    print(f"  │   │   ├── verse_1.json")
    print(f"  │   │   ├── verse_2.json")
    print(f"  │   │   └── ...")
    print(f"  ├── ar-tafsir-muyassar/")
    print(f"  └── ...")
    print("=" * 70)

def create_metadata():
    """Create metadata file"""
    tafsirs = get_tafsirs_list() or []
    
    tafsir_list = []
    for tafsir in tafsirs:
        tafsir_list.append({
            "id": tafsir.get('id'),
            "slug": tafsir.get('slug'),
            "name": tafsir.get('name'),
            "language": tafsir.get('language_name'),
            "author": tafsir.get('author_name')
        })
    
    metadata = {
        "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "method": "Quran.com API (Parallel)",
        "workers": MAX_WORKERS,
        "total_chapters": TOTAL_CHAPTERS,
        "structure": "tafsirKey/chapter_N/verse_M.json",
        "app_structure": "matches Quran v4 app exactly",
        "tafsirs": tafsir_list,
        "total_tafsirs": len(tafsir_list),
        "ready_to_upload": "Yes - copy tafsir_data folder to QuranTranslations repo"
    }
    
    metadata_path = OUTPUT_DIR / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 Metadata: {metadata_path}")

if __name__ == "__main__":
    print("\n" + "⚡ QURAN TAFSIR DOWNLOADER - APP STRUCTURE ⚡".center(70))
    print(f"Output: {OUTPUT_DIR.absolute()}\n")
    
    try:
        download_all_tafsirs()
        create_metadata()
        
        print("\n✨ SUCCESS!")
        print("Next steps:")
        print("  1. Copy 'tafsir_data' folder to your QuranTranslations repo")
        print("  2. Commit & push to GitHub")
        print("  3. Update your app's API to point to your repo")
        print("  4. Users download from your server instead!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")