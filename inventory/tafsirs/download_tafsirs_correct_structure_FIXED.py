#!/usr/bin/env python3
"""
Download tafsirs from Quran.com API - FIXED VERSION
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE_URL = "https://api.quran.com/api/v4"
OUTPUT_DIR = Path("./tafsir_data")
TOTAL_CHAPTERS = 114
MAX_WORKERS = 5
REQUEST_TIMEOUT = 10

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_tafsirs_list() -> Optional[List[Dict]]:
    """Fetch list of available tafsirs"""
    try:
        print("📥 Fetching tafsirs list...")
        url = f"{API_BASE_URL}/resources/tafsirs"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        tafsirs = data.get('tafsirs', [])
        print(f"✅ Found {len(tafsirs)} tafsirs\n")
        
        return tafsirs
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_tafsir_data(tafsir_id: int, chapter: int, verse: int) -> Optional[Dict]:
    """Fetch tafsir data - CORRECT endpoint"""
    try:
        # CORRECT endpoint: /tafsirs/{id}/{chapter}:{verse}
        verse_key = f"{chapter}:{verse}"
        url = f"{API_BASE_URL}/tafsirs/{tafsir_id}/{verse_key}"
        
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        data = response.json()
        
        # Extract tafsir from response
        if 'tafsir' in data:
            return data['tafsir']
        
        return None
    except:
        return None

def save_tafsir_verse(tafsir_key: str, chapter: int, verse: int, data: Dict) -> bool:
    """Save tafsir verse"""
    try:
        tafsir_dir = OUTPUT_DIR / tafsir_key / f"chapter_{chapter}"
        tafsir_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = tafsir_dir / f"verse_{verse}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except:
        return False

def download_single_verse(args: tuple) -> tuple:
    """Download single verse"""
    tafsir_id, tafsir_key, chapter, verse = args
    
    data = get_tafsir_data(tafsir_id, chapter, verse)
    
    if data is None or not data.get('text'):
        return (tafsir_key, chapter, verse, False, 0)
    
    success = save_tafsir_verse(tafsir_key, chapter, verse, data)
    return (tafsir_key, chapter, verse, success, 1 if success else 0)

def download_tafsir_parallel(tafsir_id: int, tafsir_key: str, tafsir_name: str) -> int:
    """Download all verses for a tafsir"""
    
    print(f"📖 {tafsir_name} (ID: {tafsir_id})")
    
    download_tasks = []
    for chapter in range(1, TOTAL_CHAPTERS + 1):
        for verse in range(1, 300):
            download_tasks.append((tafsir_id, tafsir_key, chapter, verse))
    
    total_downloaded = 0
    chapters_with_verses = set()
    completed_tasks = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_single_verse, task): task for task in download_tasks}
        
        for future in as_completed(futures):
            completed_tasks += 1
            
            try:
                _, chapter, verse, success, count = future.result()
                
                if success:
                    total_downloaded += count
                    chapters_with_verses.add(chapter)
                
                if completed_tasks % 500 == 0:
                    progress = (completed_tasks / len(download_tasks)) * 100
                    print(f"  [{progress:5.1f}%] {total_downloaded:6d} verses", end='\r')
                    
            except:
                pass
    
    chapters = len(chapters_with_verses)
    print(f"  ✅ {total_downloaded:6d} verses in {chapters:3d} chapters" + " " * 30)
    
    return total_downloaded

def download_all_tafsirs():
    """Download all tafsirs"""
    
    tafsirs = get_tafsirs_list()
    if not tafsirs:
        return
    
    print("=" * 70)
    print(f"⚡ Downloading {len(tafsirs)} tafsirs (Parallel mode)")
    print("=" * 70 + "\n")
    
    start_time = time.time()
    total_verses = 0
    success_count = 0
    
    for idx, tafsir in enumerate(tafsirs, 1):
        tafsir_id = tafsir.get('id')
        tafsir_slug = tafsir.get('slug')
        tafsir_name = tafsir.get('name', tafsir_slug)
        
        if not tafsir_id:
            continue
        
        print(f"[{idx:2d}/{len(tafsirs)}] ", end='')
        
        try:
            downloaded = download_tafsir_parallel(tafsir_id, tafsir_slug, tafsir_name)
            
            if downloaded > 0:
                total_verses += downloaded
                success_count += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    
    print("\n" + "=" * 70)
    print(f"✅ Downloaded: {total_verses:,} verses from {success_count} tafsirs")
    print(f"⏱️  Time: {hours}h {minutes}m")
    print(f"📁 Output: {OUTPUT_DIR.absolute()}")
    print("=" * 70)

if __name__ == "__main__":
    print("\n⚡ TAFSIR DOWNLOADER (FIXED)\n")
    
    try:
        download_all_tafsirs()
        print("\n✨ Done!\n")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")