#!/usr/bin/env python3
"""
Download all Tafsir texts from the Qur'an API - PARALLEL VERSION (FIXED)
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
OUTPUT_DIR = Path("./tafsir_data")
TOTAL_CHAPTERS = 114
MAX_WORKERS = 5
REQUEST_TIMEOUT = 10

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def test_tafsir_slug(slug: str) -> bool:
    """Test if a tafsir slug works by trying to fetch one verse"""
    try:
        url = f"{API_BASE_URL}/tafsirs/{slug}/1:1"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_tafsirs_list() -> Optional[List[Dict]]:
    """Fetch list of available tafsirs"""
    try:
        print("📥 Fetching tafsirs list...")
        url = f"{API_BASE_URL}/resources/tafsirs"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        tafsirs = data.get('tafsirs', [])
        print(f"✅ Found {len(tafsirs)} tafsirs available\n")
        
        # Test each slug and find the correct one
        print("🔍 Testing tafsir slugs to find working ones...")
        for tafsir in tafsirs:
            original_slug = tafsir.get('slug')
            tafsir_name = tafsir.get('name')
            
            # Test original slug
            if test_tafsir_slug(original_slug):
                print(f"  ✅ {tafsir_name}: {original_slug}")
            else:
                # Try without common prefixes
                test_slugs = [
                    original_slug.replace('tafisr-', 'tafsir-'),
                    original_slug.replace('en-tafisr-', 'en-tafsir-'),
                    original_slug.replace('ar-tafsir-', 'ar-'),
                ]
                
                found = False
                for test_slug in test_slugs:
                    if test_tafsir_slug(test_slug):
                        tafsir['slug'] = test_slug  # Update with working slug
                        print(f"  ✅ {tafsir_name}: {test_slug} (corrected from {original_slug})")
                        found = True
                        break
                
                if not found:
                    print(f"  ❌ {tafsir_name}: No working slug found ({original_slug})")
        
        print()
        return tafsirs
    except Exception as e:
        print(f"❌ Error fetching tafsirs: {e}")
        return None

def get_tafsir_data(tafsir_slug: str, chapter: int, verse: int) -> Optional[Dict]:
    """Fetch tafsir data for a specific verse"""
    try:
        verse_key = f"{chapter}:{verse}"
        url = f"{API_BASE_URL}/tafsirs/{tafsir_slug}/{verse_key}"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except:
        return None

def save_tafsir_verse(tafsir_key: str, chapter: int, verse: int, data: Dict) -> bool:
    """Save tafsir verse data to file"""
    tafsir_dir = OUTPUT_DIR / tafsir_key / f"chapter_{chapter}"
    tafsir_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = tafsir_dir / f"verse_{verse}.json"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return False

def download_single_verse(args: tuple) -> tuple:
    """Download a single verse"""
    tafsir_slug, tafsir_key, chapter, verse = args
    
    data = get_tafsir_data(tafsir_slug, chapter, verse)
    
    if data is None:
        return (tafsir_key, chapter, verse, False, 0)
    
    tafsir_content = data.get('tafsir') if isinstance(data, dict) else data
    
    if tafsir_content and isinstance(tafsir_content, dict) and tafsir_content.get('text'):
        success = save_tafsir_verse(tafsir_key, chapter, verse, tafsir_content)
        return (tafsir_key, chapter, verse, success, 1)
    
    return (tafsir_key, chapter, verse, False, 0)

def download_tafsir_parallel(tafsir_slug: str, tafsir_key: str, tafsir_name: str) -> int:
    """Download all verses for a tafsir using parallel downloads"""
    
    print(f"\n📖 Downloading: {tafsir_name}")
    print(f"   Slug: {tafsir_slug}")
    print(f"   Using {MAX_WORKERS} parallel workers...")
    
    # Create list of all (chapter, verse) pairs
    download_tasks = []
    for chapter in range(1, TOTAL_CHAPTERS + 1):
        for verse in range(1, 300):
            download_tasks.append((tafsir_slug, tafsir_key, chapter, verse))
    
    total_downloaded = 0
    chapters_with_verses = set()
    completed_tasks = 0
    
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
                
                if completed_tasks % 500 == 0:
                    progress = (completed_tasks / len(download_tasks)) * 100
                    print(f"   [{progress:5.1f}%] {total_downloaded:6d} verses", end='\r')
                    
            except Exception as e:
                pass
    
    chapters_with_content = len(chapters_with_verses)
    print(f"   ✅ Total: {total_downloaded:6d} verses in {chapters_with_content:3d} chapters" + " " * 20)
    
    return total_downloaded

def download_all_tafsirs():
    """Download all available tafsirs"""
    
    tafsirs = get_tafsirs_list()
    if not tafsirs:
        print("❌ Failed to fetch tafsirs list")
        return
    
    print("=" * 70)
    print(f"🎯 Starting PARALLEL download of available tafsirs")
    print("=" * 70)
    
    start_time = time.time()
    total_verses_all = 0
    successful_tafsirs = 0
    failed_tafsirs = 0
    
    for idx, tafsir in enumerate(tafsirs, 1):
        tafsir_slug = tafsir.get('slug')
        tafsir_name = tafsir.get('name', tafsir_slug)
        tafsir_lang = tafsir.get('language_name', 'Unknown')
        
        if not tafsir_slug:
            continue
        
        print(f"\n[{idx}/{len(tafsirs)}] {tafsir_name} ({tafsir_lang})")
        
        try:
            downloaded = download_tafsir_parallel(tafsir_slug, tafsir_slug, tafsir_name)
            
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
    print(f"✅ Successful: {successful_tafsirs} | ❌ Failed: {failed_tafsirs}")
    print(f"📝 Total verses: {total_verses_all:,}")
    print(f"⏱️  Time: {hours}h {minutes}m")
    print(f"📁 Output: {OUTPUT_DIR.absolute()}")
    print("=" * 70)

if __name__ == "__main__":
    print("\n" + "⚡ QUR'AN TAFSIR PARALLEL DOWNLOADER (FIXED) ⚡".center(70))
    print(f"Output: {OUTPUT_DIR.absolute()}\n")
    
    try:
        download_all_tafsirs()
        print("\n✨ Done!\n")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")