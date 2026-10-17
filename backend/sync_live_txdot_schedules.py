import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

"""
Amestx TxDOT Live Schedules & Estimates Synchronizer
===================================================
Queries official TxDOT live datasets on data.texas.gov (Socrata) & Tableau:
1. drau-zphx: TxDOT Scheduled & Future Lettings (Project Tracker)
2. qh8x-rm8r: TxDOT Pre-Bid Official Items & Notices
3. de7b-7dna: TxDOT Completed & Active Lettings
4. tableau.txdot.gov: Notice to Contractors & Project Information Dashboard

Synchronizes:
- Official bid dates (catches all addenda, extensions, and rescheduling)
- Engineer's estimates
- Project titles, counties, highways, and classifications
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
    os.path.join(r"C:\Users\fibrg\Desktop\Amestx Estimator App", 'downloads'),
    os.path.join(r"C:\Users\fibrg\Desktop\Amestx Estimator App", 'data', 'downloads'),
    os.path.join(r"C:\Users\fibrg\Desktop\Amestx Estimator App", 'frontend', 'downloads'),
    os.path.join(r"C:\Users\fibrg\Desktop\Amestx Estimator App", 'frontend', 'public', 'downloads'),
]

def query_socrata(resource_id, where_clause, limit=5000):
    url = f"https://data.texas.gov/resource/{resource_id}.json?$where={urllib.parse.quote(where_clause)}&$limit={limit}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"  [WARN] Query failed for {resource_id}: {e}")
        return []

def format_date_str(iso_str):
    if not iso_str:
        return None
    try:
        dt_part = iso_str.split('T')[0]
        parts = dt_part.split('-')
        return f"{parts[1]}/{parts[2]}/{parts[0]}"
    except Exception:
        return None

def sync_month(month_str="2026-10"):
    print(f"\n=======================================================")
    print(f"  SYNCHRONIZING TXDOT SCHEDULES & DATES: {month_str}")
    print(f"=======================================================")

    year = int(month_str.split('-')[0])
    m_num = int(month_str.split('-')[1])
    next_year = year + 1 if m_num == 12 else year
    next_m = "01" if m_num == 12 else f"{m_num + 1:02d}"

    start_date = f"{month_str}-01T00:00:00"
    end_date = f"{next_year}-{next_m}-01T00:00:00"

    # Find the primary cache file
    cache_file = os.path.join(BASE_DIR, 'downloads', f"monthly_cache_{month_str}.json")
    if not os.path.exists(cache_file):
        cache_file = os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'downloads', f"monthly_cache_{month_str}.json")

    if not os.path.exists(cache_file):
        print(f"[ERROR] Cache file not found: {cache_file}")
        return 0

    with open(cache_file, 'r', encoding='utf-8-sig') as f:
        projects = json.load(f)

    print(f"Loaded {len(projects)} projects from cache: {os.path.basename(cache_file)}")

    # 1. Fetch live scheduled lettings from drau-zphx
    print(f"Querying TxDOT drau-zphx (Scheduled Lettings)...")
    q_sched = f"(project_estimated_let_date >= '{start_date}' and project_estimated_let_date < '{end_date}') or (project_approved_let_date >= '{start_date}' and project_approved_let_date < '{end_date}') or (bid_received_until_date_and >= '{start_date}' and bid_received_until_date_and < '{end_date}')"
    live_sched = query_socrata("drau-zphx", q_sched, limit=5000)
    print(f"Retrieved {len(live_sched)} live scheduled rows from drau-zphx.")

    # 2. Fetch completed/active let projects from de7b-7dna
    print(f"Querying TxDOT de7b-7dna (Completed / Let Projects)...")
    q_let = f"project_actual_let_date >= '{start_date}' and project_actual_let_date < '{end_date}'"
    live_let = query_socrata("de7b-7dna", q_let, limit=5000)
    print(f"Retrieved {len(live_let)} live let rows from de7b-7dna.")

    # Build master live map indexed by CSJ and CCSJ
    live_map = {}
    for r in live_sched:
        csj = r.get('control_section_job_csj')
        ccsj = r.get('controlling_project_id_ccsj') or csj
        d_raw = r.get('bid_received_until_date_and') or r.get('project_approved_let_date') or r.get('project_estimated_let_date')
        d_fmt = format_date_str(d_raw)
        
        est = 0.0
        for est_field in ('sealed_engineer_s_estimate', 'sealed_engineer_s_estimate_1', 'project_estimate_low_bid'):
            if r.get(est_field):
                try:
                    v = float(r.get(est_field))
                    if v > 0:
                        est = v
                        break
                except Exception:
                    pass

        entry = {
            'date': d_fmt,
            'estimate': est,
            'county': r.get('county'),
            'highway': r.get('highway'),
            'projectType': r.get('type_of_work') or r.get('project_classification') or r.get('project_description'),
            'source': 'drau-zphx'
        }
        if csj:
            live_map[csj] = entry
        if ccsj and ccsj not in live_map:
            live_map[ccsj] = entry

    for r in live_let:
        csj = r.get('control_section_job_csj')
        ccsj = r.get('controlling_project_id_ccsj') or csj
        d_raw = r.get('project_actual_let_date')
        d_fmt = format_date_str(d_raw)

        est = 0.0
        for est_field in ('sealed_engineer_s_estimate', 'sealed_engineer_s_estimate_1'):
            if r.get(est_field):
                try:
                    v = float(r.get(est_field))
                    if v > 0:
                        est = v
                        break
                except Exception:
                    pass

        entry = {
            'date': d_fmt,
            'estimate': est,
            'county': r.get('county'),
            'highway': r.get('highway'),
            'projectType': r.get('project_classification') or r.get('short_description'),
            'source': 'de7b-7dna'
        }
        if csj:
            live_map[csj] = entry
        if ccsj and ccsj not in live_map:
            live_map[ccsj] = entry

    # Update projects in cache
    updates_count = 0
    date_fixes = []

    for p in projects:
        csj = p.get('csj')
        sub_csjs = p.get('subCSJs', [])
        
        # Check primary CSJ or any subCSJ
        match_entry = live_map.get(csj)
        if not match_entry:
            for sc in sub_csjs:
                if sc in live_map:
                    match_entry = live_map[sc]
                    break

        if match_entry:
            # Check letDate
            live_date = match_entry.get('date')
            curr_date = p.get('letDate')
            if live_date and curr_date != live_date:
                date_fixes.append(f"  CSJ {csj}: {curr_date} -> {live_date} ({match_entry.get('source')})")
                p['letDate'] = live_date
                updates_count += 1

            # Check estimate if current is 0
            live_est = match_entry.get('estimate', 0.0)
            curr_est = float(p.get('estimate') or 0.0)
            if curr_est == 0 and live_est > 0:
                p['estimate'] = live_est
                updates_count += 1

    print(f"\nApplied {len(date_fixes)} date corrections:")
    for df in date_fixes[:20]:
        print(df)
    if len(date_fixes) > 20:
        print(f"  ... and {len(date_fixes) - 20} more date corrections.")

    # Save updated cache across all destination paths
    saved_dirs = set()
    for d in DOWNLOADS_DIRS:
        if os.path.exists(d):
            dest_file = os.path.join(d, f"monthly_cache_{month_str}.json")
            try:
                with open(dest_file, 'w', encoding='utf-8') as f:
                    json.dump(projects, f, indent=2)
                saved_dirs.add(dest_file)
            except Exception as e:
                print(f"  [ERROR] Failed to save {dest_file}: {e}")

    print(f"\nSaved updated cache to {len(saved_dirs)} locations:")
    for sd in saved_dirs:
        print(f"  [OK] {sd}")

    return len(date_fixes)

if __name__ == "__main__":
    total_fixes = 0
    for m in ["2026-10", "2026-11", "2026-12"]:
        total_fixes += sync_month(m)
    print(f"\n=======================================================")
    print(f"  TOTAL DATE CORRECTIONS APPLIED ACROSS ALL MONTHS: {total_fixes}")
    print(f"=======================================================\n")
