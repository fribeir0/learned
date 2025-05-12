import subprocess
import json

def run_nuclei_scan(targets_file):
    result = subprocess.run(
        ["nuclei", "-l", targets_file, "-json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    
    vulns_by_ip = {}
    for line in result.stdout.decode().splitlines():
        try:
            vuln = json.loads(line)
            ip = vuln["host"].split(":")[0]
            if ip not in vulns_by_ip:
                vulns_by_ip[ip] = []
            vulns_by_ip[ip].append({
                "template": vuln.get("template", ""),
                "cve": vuln.get("info", {}).get("reference", []),
                "severity": vuln.get("info", {}).get("severity", ""),
                "description": vuln.get("info", {}).get("name", "")
            })
        except:
            pass
    return vulns_by_ip
