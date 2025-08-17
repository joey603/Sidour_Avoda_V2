#!/usr/bin/env python3

import json
from urllib.request import Request, urlopen

GITHUB_OWNER = "joey603"
GITHUB_REPO = "Sidour_Avoda_V2"

def test_github_connection():
    try:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
        print(f"Testing connection to: {url}")
        
        req = Request(url, headers={"User-Agent": "SidourAvodaUpdater"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        
        print(f"Response status: {resp.status}")
        print(f"Response headers: {dict(resp.headers)}")
        
        tag = str(data.get("tag_name") or "").strip()
        print(f"Found tag: {tag}")
        
        assets = data.get("assets") or []
        print(f"Found {len(assets)} assets:")
        
        for i, asset in enumerate(assets):
            name = asset.get("name", "")
            download_url = asset.get("browser_download_url", "")
            print(f"  {i+1}. {name} -> {download_url}")
        
        return tag, assets
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    test_github_connection()
