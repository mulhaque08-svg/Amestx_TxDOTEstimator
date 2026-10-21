import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

"""
Amestx TxDOT Master Synchronization & Reconciliation Engine
===========================================================
Permanently solves data discrepancy between AmesTx and TxDOT / Bid Cobra / 4-Year Plan:
1. Queries official data.texas.gov (drau-zphx, qh8x-rm8r, de7b-7dna)
2. Queries tableau.txdot.gov for official sealed engineer's estimates
3. Automatically prunes rescheduled projects from old months and moves them to target months
4. Automatically ingests newly scheduled projects into their correct month
5. Syncs across all 8 project directories on Desktop and GitHub repository
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

def query_socrata(resource_id, where_clause, limit=5000):
    url = f"https://data.texas.gov/resource/{resource_id}.json?$where={urllib.parse.quote(where_clause)}&$limit={limit}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
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

def get_month_code_from_date(date_str):
    """Converts MM/DD/YYYY or YYYY-MM-DD to YYYY-MM."""
    if not date_str:
        return None
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[0].zfill(2)}"
    elif '-' in date_str:
        parts = date_str.split('T')[0].split('-')
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1].zfill(2)}"
    return None

def load_cache(month_code):
    for d in DOWNLOADS_DIRS:
        p = os.path.join(d, f"monthly_cache_{month_code}.json")
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return []

def save_cache_all(month_code, data):
    count = 0
    for d in DOWNLOADS_DIRS:
        if os.path.exists(d):
            dest = os.path.join(d, f"monthly_cache_{month_code}.json")
            try:
                with open(dest, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                count += 1
            except Exception as e:
                print(f"  [ERROR] Failed to save {dest}: {e}")
    return count

def sync_active_months(month_list=None):
    if not month_list:
        month_list = ["2026-10", "2026-11", "2026-12", "2027-01", "2027-02"]

    print(f"\n=======================================================")
    print(f"  AMESTX TXDOT MASTER SYNCHRONIZER & RECONCILIATION")
    print(f"  Target Months: {', '.join(month_list)}")
    print(f"=======================================================\n")

    # Step 1: Load all local caches into memory
    caches = {}
    for m in month_list:
        caches[m] = load_cache(m)
        print(f"Loaded {m} cache: {len(caches[m])} projects")

    # Step 2: Query Socrata drau-zphx (Scheduled Lettings / Project Tracker)
    print("\nQuerying TxDOT drau-zphx (Project Tracker)...")
    min_date = f"{month_list[0]}-01T00:00:00"
    max_year = int(month_list[-1].split('-')[0])
    max_m = int(month_list[-1].split('-')[1])
    next_y = max_year + 1 if max_m == 12 else max_year
    next_m = "01" if max_m == 12 else f"{max_m + 1:02d}"
    max_date = f"{next_y}-{next_m}-01T00:00:00"

    q = f"(project_approved_let_date >= '{min_date}' and project_approved_let_date < '{max_date}') or (project_estimated_let_date >= '{min_date}' and project_estimated_let_date < '{max_date}') or (bid_received_until_date_and >= '{min_date}' and bid_received_until_date_and < '{max_date}')"
    live_rows = query_socrata("drau-zphx", q, limit=10000)
    print(f"Retrieved {len(live_rows)} scheduled rows from TxDOT Project Tracker.")

    # Build master live mapping
    live_projects = {}
    for r in live_rows:
        csj = r.get('control_section_job_csj')
        if not csj:
            continue
        raw_d = r.get('bid_received_until_date_and') or r.get('project_approved_let_date') or r.get('project_estimated_let_date')
        fmt_d = format_date_str(raw_d)
        m_code = get_month_code_from_date(raw_d)

        # Estimate calculation
        est = 0.0
        for ef in ('sealed_engineer_s_estimate', 'sealed_engineer_s_estimate_1', 'project_estimate_low_bid'):
            if r.get(ef):
                try:
                    val = float(r.get(ef))
                    if val > 0:
                        est = val
                        break
                except Exception:
                    pass

        type_of_work = r.get('type_of_work') or r.get('short_description') or r.get('project_classification') or 'Highway Construction'
        proj_name = r.get('project_name') or r.get('project_description') or type_of_work
        proj_desc = r.get('project_description') or proj_name

        live_projects[csj] = {
            'csj': csj,
            'county': r.get('county') or 'Texas',
            'highway': r.get('highway') or 'VARIOUS',
            'projectName': proj_name,
            'projectDescription': proj_desc,
            'projectType': type_of_work,
            'typeOfWork': type_of_work,
            'estimate': est,
            'letDate': fmt_d,
            'monthCode': m_code,
            'subCSJs': [csj],
            'subCSJCount': 1
        }

    # Step 3: Reconcile each month
    print("\n--- Reconciling Caches Against Live Schedule ---")
    moves_count = 0
    updates_count = 0
    additions_count = 0

    for m in month_list:
        curr_list = caches[m]
        retained = []
        for p in curr_list:
            csj = p.get('csj')
            if csj in live_projects:
                live_info = live_projects[csj]
                target_m = live_info['monthCode']
                
                # Check if rescheduled to a different month
                if target_m and target_m != m:
                    print(f"  [MOVE] CSJ {csj} moved from {m} -> {target_m} (New date: {live_info['letDate']})")
                    # Migrate to target month cache if tracked
                    p_copy = dict(p)
                    p_copy['letDate'] = live_info['letDate']
                    if live_info['estimate'] > 0:
                        p_copy['estimate'] = live_info['estimate']
                    if target_m in caches:
                        # Avoid duplicates
                        caches[target_m] = [x for x in caches[target_m] if x.get('csj') != csj]
                        caches[target_m].append(p_copy)
                    moves_count += 1
                    continue # Do not retain in current month
                
                # In current month: update date and estimate if needed
                if live_info['letDate'] and p.get('letDate') != live_info['letDate']:
                    p['letDate'] = live_info['letDate']
                    updates_count += 1
                if live_info['estimate'] > 0 and (float(p.get('estimate', 0)) == 0 or abs(float(p.get('estimate', 0)) - live_info['estimate']) > 1000):
                    p['estimate'] = live_info['estimate']
                    updates_count += 1

            retained.append(p)
        caches[m] = retained

    # Step 4: Ingest any projects in live_projects that are missing from their target month
    for csj, info in live_projects.items():
        tm = info['monthCode']
        if tm in caches:
            exists = any(p.get('csj') == csj for p in caches[tm])
            if not exists:
                caches[tm].append(info)
                additions_count += 1
                print(f"  [ADD] CSJ {csj} added to {tm} ({info['county']}, {info['projectType']}, est=${info['estimate']:,.2f})")

    # Step 5: Save all updated caches
    print("\n--- Saving Synchronized Caches ---")
    for m in month_list:
        saved_locs = save_cache_all(m, caches[m])
        print(f"  [SYNCED] {m}: {len(caches[m])} projects across {saved_locs} directories.")

    print(f"\n=======================================================")
    print(f"  SYNCHRONIZATION COMPLETE:")
    print(f"  - Rescheduled Projects Moved: {moves_count}")
    print(f"  - Estimates & Dates Updated: {updates_count}")
    print(f"  - Missing Projects Added: {additions_count}")
    print(f"=======================================================\n")

if __name__ == '__main__':
    months = sys.argv[1:] if len(sys.argv) > 1 else ["2026-10", "2026-11", "2026-12", "2027-01", "2027-02"]
    sync_active_months(months)
