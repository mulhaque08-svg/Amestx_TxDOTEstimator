import os
import re
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

"""
TxDOT FTP Plan & Proposal Live Synchronizer
===========================================
Crawls official TxDOT FTP web listings across categories:
- State-Let-Construction
- State-Let-Maintenance
- Local-Let-Maintenance

Extracts exact CSJ direct PDF links for both Proposals and Plans,
and compiles:
1. downloads/ftp_map_{YYYY-MM}.json
2. downloads/ftp_proposals_map_{YYYY-MM}.json
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIRS = [
    os.path.join(BASE_DIR, 'downloads'),
    os.path.join(BASE_DIR, 'data', 'downloads'),
    os.path.join(BASE_DIR, 'frontend', 'downloads'),
    os.path.join(BASE_DIR, 'frontend', 'public', 'downloads'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'downloads'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'data', 'downloads'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'frontend', 'downloads'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'frontend', 'public', 'downloads'),
]

CSJ_REGEX = re.compile(r'(\d{4}-\d{2}-\d{3})')
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

CATEGORIES = [
    'State-Let-Construction',
    'State-Let-Maintenance',
    'Local-Let-Maintenance'
]

def fetch_links_from_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=[\"\']([^\"\']+\.pdf)[\"\']', html, re.I)
            return links
    except Exception as e:
        return []

def sync_month_ftp_map(year=2026, month_num=11):
    month_str = f"{month_num:02d}"
    month_name = MONTH_NAMES[month_num - 1]
    month_folder = f"{month_str} {month_name}"
    month_key = f"{year}-{month_str}"

    print(f"\nScanning TxDOT FTP for {month_key} ({month_folder})...")

    # Load existing maps if available to merge
    ftp_map = {}
    proposals_map = {}

    local_primary_map = os.path.join(BASE_DIR, 'downloads', f'ftp_map_{month_key}.json')
    if os.path.exists(local_primary_map):
        try:
            with open(local_primary_map, 'r', encoding='utf-8-sig') as f:
                ftp_map = json.load(f)
        except Exception:
            ftp_map = {}

    local_primary_prop = os.path.join(BASE_DIR, 'downloads', f'ftp_proposals_map_{month_key}.json')
    if os.path.exists(local_primary_prop):
        try:
            with open(local_primary_prop, 'r', encoding='utf-8-sig') as f:
                proposals_map = json.load(f)
        except Exception:
            proposals_map = {}

    for cat in CATEGORIES:
        # Proposals URL
        prop_dir = f"{month_str} Proposal" if cat == 'Local-Let-Maintenance' else f"{month_str} Proposals"
        url_prop = f"https://ftp.txdot.gov/plans/{cat}/{year}/{urllib.parse.quote(month_folder)}/{urllib.parse.quote(prop_dir)}/"
        
        # Plans URL
        plan_dir = f"{month_str} Plans"
        url_plan = f"https://ftp.txdot.gov/plans/{cat}/{year}/{urllib.parse.quote(month_folder)}/{urllib.parse.quote(plan_dir)}/"

        # Crawl proposals
        prop_links = fetch_links_from_url(url_prop)
        print(f"  [{cat}] Proposals found: {len(prop_links)}")
        for link in prop_links:
            dec = urllib.parse.unquote(link).strip()
            # Clean leading slash or query params
            if dec.startswith('/'):
                dec = dec.split('/')[-1]
            m = CSJ_REGEX.search(dec)
            if m:
                csj = m.group(1)
                full_url = urllib.parse.urljoin(url_prop, link)
                
                proposals_map[csj] = {
                    'proposalUrl': full_url,
                    'proposalName': dec
                }
                
                if csj not in ftp_map:
                    ftp_map[csj] = {}
                ftp_map[csj]['proposalUrl'] = full_url
                ftp_map[csj]['proposalName'] = dec

        # Crawl plans
        plan_links = fetch_links_from_url(url_plan)
        print(f"  [{cat}] Plans found: {len(plan_links)}")
        for link in plan_links:
            dec = urllib.parse.unquote(link).strip()
            if dec.startswith('/'):
                dec = dec.split('/')[-1]
            m = CSJ_REGEX.search(dec)
            if m:
                csj = m.group(1)
                full_url = urllib.parse.urljoin(url_plan, link)
                
                if csj not in ftp_map:
                    ftp_map[csj] = {}
                
                # Check for volume 2, volume 3, etc.
                if 'vol' in dec.lower() or 'volume' in dec.lower():
                    if 'planVolumes' not in ftp_map[csj]:
                        ftp_map[csj]['planVolumes'] = []
                    ftp_map[csj]['planVolumes'].append({
                        'title': dec,
                        'url': full_url
                    })
                
                # If first plan or main plan
                if 'planUrl' not in ftp_map[csj] or not ('vol' in dec.lower()):
                    ftp_map[csj]['planUrl'] = full_url
                    ftp_map[csj]['planName'] = dec

    print(f"Total Unique CSJs with Proposals ({month_key}): {len(proposals_map)}")
    print(f"Total Unique CSJs with Plans/Proposals in FTP map ({month_key}): {len(ftp_map)}")

    # Write to all download directories
    for d in DOWNLOADS_DIRS:
        if os.path.exists(d):
            p_map_file = os.path.join(d, f'ftp_map_{month_key}.json')
            p_prop_file = os.path.join(d, f'ftp_proposals_map_{month_key}.json')
            try:
                with open(p_map_file, 'w', encoding='utf-8') as f:
                    json.dump(ftp_map, f, indent=2)
                with open(p_prop_file, 'w', encoding='utf-8') as f:
                    json.dump(proposals_map, f, indent=2)
            except Exception as e:
                print(f"Error writing to {d}: {e}")

    return ftp_map, proposals_map

if __name__ == '__main__':
    # Sync October 2026, November 2026, and December 2026
    for m in [10, 11, 12]:
        sync_month_ftp_map(2026, m)
