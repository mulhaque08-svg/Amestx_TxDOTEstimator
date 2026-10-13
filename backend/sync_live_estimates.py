import os
import json
import csv
import re
import urllib.request
import concurrent.futures
import time

"""
TxDOT Live Estimate Synchronizer & Verification Engine
======================================================
Queries TxDOT's live Tableau Server endpoints:
1. Notice to Contractors (Maintenance, Materials, Local Let)
2. Project Information Dashboard (Statewide Let Highway Construction)

Compares every project's estimate against the live official TxDOT Tableau data,
detects addendums/updates, and updates all cache & application files automatically.
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

APP_HTML_PATHS = [
    os.path.join(BASE_DIR, 'app.html'),
    os.path.join(BASE_DIR, 'frontend', 'app.html'),
    os.path.join(BASE_DIR, 'frontend', 'public', 'app.html'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'app.html'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'frontend', 'app.html'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'frontend', 'public', 'app.html'),
]

PROJECTS_JSON_PATHS = [
    os.path.join(BASE_DIR, 'data', 'projects.json'),
    os.path.join(r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator", 'data', 'projects.json'),
]

def fetch_live_txdot_estimate(csj):
    clean_csj = csj.strip()
    
    # 1. Try Notice to Contractors (Maintenance / Materials / Local Let)
    u_notice = f"https://tableau.txdot.gov/views/ProjectInformationDashboard/NoticetoContractors.csv?Controlling%20Project%20Id%20(Ccsj)={clean_csj}"
    try:
        req = urllib.request.Request(u_notice, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            lines = [l.strip() for l in resp.read().decode('utf-8', errors='ignore').split('\n') if l.strip()]
            if len(lines) > 1:
                reader = csv.reader([lines[-1]])
                row = next(reader)
                if len(row) >= 3:
                    raw_val = row[2].replace('$', '').replace(',', '').strip()
                    val = float(raw_val)
                    if val > 0:
                        return val, 'NoticeToContractors'
    except Exception:
        pass

    # 2. Try Project Information Dashboard (Statewide Let / CST)
    u_cst = f"https://tableau.txdot.gov/views/ProjectInformationDashboard/ProjectInformationDashboard.csv?Controlling%20Project%20Id%20(Ccsj)={clean_csj}"
    try:
        req = urllib.request.Request(u_cst, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            lines = [l.strip() for l in resp.read().decode('utf-8', errors='ignore').split('\n') if l.strip()]
            if len(lines) > 1:
                reader = csv.reader([lines[-1]])
                row = next(reader)
                if len(row) >= 2:
                    raw_val = row[1].replace('$', '').replace(',', '').strip()
                    val = float(raw_val)
                    if val > 0:
                        return val, 'ProjectInformationDashboard'
    except Exception:
        pass

    return None, None

def sync_month_estimates(month='2026-10'):
    print(f"\n=======================================================")
    print(f"  AMESTX LIVE TXDOT ESTIMATE SYNCHRONIZER ({month})")
    print(f"=======================================================\n")
    
    primary_cache_file = os.path.join(BASE_DIR, 'downloads', f"monthly_cache_{month}.json")
    if not os.path.exists(primary_cache_file):
        print(f"[ERROR] Primary cache file not found: {primary_cache_file}")
        return

    with open(primary_cache_file, 'r', encoding='utf-8-sig') as f:
        projects = json.load(f)

    print(f"Loaded {len(projects)} projects from {month} cache.")
    print("Querying TxDOT Tableau live server concurrently (10 workers)...\n")

    updated_count = 0
    updates_log = []

    def process_project(p):
        csj = p.get('csj') or p.get('controlNumber') or ''
        curr_est = float(p.get('estimate', 0))
        live_val, src = fetch_live_txdot_estimate(csj)
        return p, csj, curr_est, live_val, src

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_project, p) for p in projects]
        for f in concurrent.futures.as_completed(futures):
            p, csj, curr_est, live_val, src = f.result()
            if live_val is not None:
                # Check if discrepancy exists (difference > $1.00)
                if abs(live_val - curr_est) > 1.0:
                    print(f" [MISMATCH DETECTED] CSJ {csj}: Current=${curr_est:,.2f} -> TxDOT Live=${live_val:,.2f} ({src})")
                    p['estimate'] = live_val
                    updated_count += 1
                    updates_log.append({
                        'csj': csj,
                        'projectName': p.get('projectName', ''),
                        'oldEstimate': curr_est,
                        'newEstimate': live_val,
                        'source': src
                    })
                else:
                    # Verified match
                    pass
            else:
                pass

    print(f"\n[SUMMARY] Audit & Live Sync Complete!")
    print(f"- Total Projects Checked: {len(projects)}")
    print(f"- Discrepancies Updated: {updated_count}\n")

    # 1. Update all monthly_cache files
    for d in DOWNLOADS_DIRS:
        if os.path.exists(d):
            c_path = os.path.join(d, f"monthly_cache_{month}.json")
            try:
                with open(c_path, 'w', encoding='utf-8') as f:
                    json.dump(projects, f, indent=2)
                print(f"  [SAVED] {c_path}")
            except Exception as e:
                print(f"  [ERROR] {c_path}: {e}")

    # 2. Update projects.json
    for pj in PROJECTS_JSON_PATHS:
        if os.path.exists(pj):
            try:
                with open(pj, 'r', encoding='utf-8') as f:
                    all_p = json.load(f)
                
                # Update by CSJ
                p_map = {p.get('csj'): p.get('estimate') for p in projects if p.get('csj')}
                changed_in_all = 0
                for item in all_p:
                    c = item.get('csj')
                    if c in p_map and item.get('estimate') != p_map[c]:
                        item['estimate'] = p_map[c]
                        changed_in_all += 1
                
                with open(pj, 'w', encoding='utf-8') as f:
                    json.dump(all_p, f, indent=2)
                print(f"  [SAVED] {pj} ({changed_in_all} items updated)")
            except Exception as e:
                print(f"  [ERROR] {pj}: {e}")

    # 3. Update app.html EMBEDDED_MONTHLY_CACHE safely without regex corruption
    for html_path in APP_HTML_PATHS:
        if os.path.exists(html_path):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    f_lines = f.readlines()
                
                replaced = False
                for i, l in enumerate(f_lines):
                    if 'window.EMBEDDED_MONTHLY_CACHE =' in l:
                        raw = l.strip().replace('window.EMBEDDED_MONTHLY_CACHE =', '').rstrip(';')
                        cache_dict = json.loads(raw)
                        cache_dict[month] = projects
                        f_lines[i] = "        window.EMBEDDED_MONTHLY_CACHE = " + json.dumps(cache_dict) + ";\n"
                        replaced = True
                        break
                
                if replaced:
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.writelines(f_lines)
                    print(f"  [SAVED] {html_path} (embedded cache updated)")
            except Exception as e:
                print(f"  [ERROR] {html_path}: {e}")

    # 4. Save updates report
    report_file = os.path.join(BASE_DIR, 'backend', f"live_sync_report_{month}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(updates_log, f, indent=2)
    print(f"  [SAVED] {report_file}\n")

if __name__ == '__main__':
    sync_month_estimates('2026-10')
