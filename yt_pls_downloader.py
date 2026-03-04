#!/usr/bin/env python3
import os
import sys
import argparse
import json
import csv
import subprocess
import shutil
import time
import random

class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# --- Utilities ---

def check_dependencies():
    if shutil.which("yt-dlp") is None:
        print(f"{Colors.RED}Error: 'yt-dlp' not found.{Colors.END}")
        sys.exit(1)

def is_playable(item):
    if item.get('is_upcoming') or item.get('live_status') == 'upcoming': return False
    if not item.get('title') or item.get('title') in ['[Deleted video]', '[Private video]']: return False
    return True

def get_meta(item):
    title = (item.get('title') or 'Untitled').replace('"', '\\"')
    url = item.get('url') or item.get('webpage_url')
    if not url and item.get('id'): url = f"https://www.youtube.com/watch?v={item.get('id')}"
    return title, url

# --- Logic ---

def download_media(items, fmt, dl_dir):
    os.makedirs(dl_dir, exist_ok=True)
    print(f"\n{Colors.YELLOW}--- Downloading {fmt.upper()} to: {dl_dir} ---{Colors.END}")
    for idx, item in enumerate(items, 1):
        title, url = get_meta(item)
        print(f"{Colors.CYAN}[{idx}/{len(items)}]{Colors.END} {title}")
        cmd = ['yt-dlp', '-o', f"{dl_dir}/%(title)s.%(ext)s", '--no-mtime', url]
        if fmt == 'mp3': cmd.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '0'])
        elif fmt == 'mp4': cmd.extend(['-f', 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]'])
        elif fmt == 'webm': cmd.extend(['-f', 'bv*[ext=webm]+ba[ext=webm]/b[ext=webm]'])
        subprocess.run(cmd)
        if idx < len(items): 
            wait = random.uniform(3, 6)
            print(f"{Colors.BLUE}Cooldown: {wait:.1f}s...{Colors.END}")
            time.sleep(wait)

def extract_data(url, flatten):
    print(f"\n{Colors.CYAN}--- Extracting Metadata ---{Colors.END}")
    cmd = ['yt-dlp', '--dump-single-json', '--flat-playlist', f"{url.rstrip('/')}/playlists"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0: return []
    data = json.loads(res.stdout).get('entries', [])
    if not flatten: return [pl for pl in data if is_playable(pl)]
    
    all_t = []
    for pl in data:
        p_url = pl.get('url') or pl.get('webpage_url')
        if p_url:
            time.sleep(1)
            sub = subprocess.run(['yt-dlp', '--dump-single-json', '--flat-playlist', p_url], capture_output=True, text=True)
            if sub.returncode == 0: all_t.extend([t for t in json.loads(sub.stdout).get('entries', []) if is_playable(t)])
    return all_t

# --- Exporters ---

def save_pls(items, path, fmt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        if fmt == 'cliamp':
            f.write("# Cliamp\n\n")
            for i in items: t, u = get_meta(i); f.write(f'[[track]]\ntitle = "{t}"\npath = "{u}"\n\n')
        elif fmt == 'm3u':
            f.write("#EXTM3U\n")
            for i in items: t, u = get_meta(i); f.write(f"#EXTINF:-1,{t}\n{u}\n")
        elif fmt == 'json':
            json.dump([{"title": get_meta(i)[0], "url": get_meta(i)[1]} for i in items], f, indent=4)
        elif fmt == 'csv':
            writer = csv.writer(f); writer.writerow(["Title", "URL"])
            for i in items: writer.writerow(get_meta(i))
    return len(items)

# --- Main ---

def main():
    check_dependencies()
    parser = argparse.ArgumentParser(description="YouTube Media Manager")
    parser.add_argument("url", help="YouTube Channel Playlists URL")
    parser.add_argument("--to-pls", choices=['cliamp', 'm3u', 'json', 'csv'], help="Playlist format")
    parser.add_argument("--download", choices=['mp3', 'mp4', 'webm'], help="Media format")
    parser.add_argument("-o", "--output", help="Path: Directory for downloads, File Path for playlist-only")
    parser.add_argument("-n", "--name", help="Playlist filename")
    parser.add_argument("-f", "--flatten", action="store_true", help="Deep scan tracks")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation plan")
    args = parser.parse_args()

    # 1. Resolve Paths
    dl_dir = None
    pls_path = None
    
    if args.download:
        dl_dir = os.path.expanduser(args.output) if args.output else os.path.join(os.getcwd(), "downloads")
        if args.to_pls:
            ext = {'cliamp': '.toml', 'm3u': '.m3u', 'json': '.json', 'csv': '.csv'}[args.to_pls]
            fname = f"{args.name}{ext}" if args.name else f"playlist{ext}"
            pls_path = os.path.join(dl_dir, fname)
    elif args.to_pls:
        ext = {'cliamp': '.toml', 'm3u': '.m3u', 'json': '.json', 'csv': '.csv'}[args.to_pls]
        if args.output:
            pls_path = os.path.expanduser(args.output)
            if not (pls_path.endswith(ext)): pls_path += ext
        else:
            def_dir = os.path.expanduser("~/.config/cliamp/playlists/") if args.to_pls == 'cliamp' else os.getcwd()
            fname = f"{args.name}{ext}" if args.name else f"export{ext}"
            pls_path = os.path.join(def_dir, fname)

    # 2. Execution Plan & Confirmation
    if not args.yes:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}--- Execution Plan ---{Colors.END}")
        print(f" {Colors.BOLD}Source URL:{Colors.END} {args.url}")
        print(f" {Colors.BOLD}Scan Mode:{Colors.END} {'Deep (Recursive)' if args.flatten else 'Quick (Playlists Only)'}")
        if dl_dir: print(f" {Colors.BOLD}Download To:{Colors.END} {dl_dir} ({args.download})")
        if pls_path: print(f" {Colors.BOLD}Playlist File:{Colors.END} {pls_path}")
        print(f"{Colors.YELLOW}----------------------{Colors.END}")
        
        confirm = input(f"Proceed? [{Colors.GREEN}{Colors.BOLD}Y{Colors.END}/n]: ").lower().strip()
        if confirm != 'y' and confirm != '':
            print(f"{Colors.RED}Aborted.{Colors.END}")
            return

    # 3. Extract Metadata
    items = extract_data(args.url, args.flatten)
    if not items:
        print(f"{Colors.RED}No playable items found.{Colors.END}"); return

    # 4. Save Playlist (PRIORITY)
    if pls_path: 
        count = save_pls(items, pls_path, args.to_pls)
        print(f"\n{Colors.GREEN}Playlist ({count} items) generated successfully: {pls_path}{Colors.END}")

    # 5. Download Media
    if dl_dir: 
        download_media(items, args.download, dl_dir)

    # 6. Fallback: Preview
    if not args.to_pls and not args.download:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}--- Found {len(items)} items ---{Colors.END}")
        for idx, item in enumerate(items, 1):
            t, _ = get_meta(item); print(f"{Colors.GREEN}{idx}.{Colors.END} {t}")

if __name__ == "__main__":
    main()