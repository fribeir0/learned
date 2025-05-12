import os
import json
from datetime import datetime

SCAN_DIR = "scan_results"

def save_scan_result(target: str, data: dict):
    os.makedirs(SCAN_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{SCAN_DIR}/{target}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_latest_scan(target: str):
    if not os.path.exists(SCAN_DIR): return None, None
    files = sorted([f for f in os.listdir(SCAN_DIR) if f.startswith(target)], reverse=True)
    if len(files) < 2: return None, None
    with open(os.path.join(SCAN_DIR, files[0]), "r") as f1, open(os.path.join(SCAN_DIR, files[1]), "r") as f2:
        return json.load(f1), json.load(f2)

def compare_scans(current: dict, previous: dict):
    diff = {}
    for key in ["subdomains", "resolved", "open_ports", "http_services", "vulnerabilities"]:
        c_set = set(current.get(key, []))
        p_set = set(previous.get(key, []))
        added = list(c_set - p_set)
        removed = list(p_set - c_set)
        if added or removed:
            diff[key] = {"added": added, "removed": removed}
    return diff
