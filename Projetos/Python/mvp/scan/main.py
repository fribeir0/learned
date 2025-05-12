from nmapScan import run_nmap_scan
from nucleiScan import run_nuclei_scan
from json_export import save_results, send_to_n8n
from config import network_range, targets_file

# 1. Scan Nmap
hosts = run_nmap_scan(network_range)

# 2. Criar lista para o Nuclei
with open(targets_file, "w") as f:
    for h in hosts:
        f.write(h["ip"] + "\n")

# 3. Scan Nuclei
vulns = run_nuclei_scan(targets_file)

# 4. Anexar vulnerabilidades aos hosts
for h in hosts:
    h["vulnerabilities"] = vulns.get(h["ip"], [])

# 5. Salvar JSON
json_data = save_results(network_range, hosts)

# 6. Enviar para n8n
send_to_n8n(json_data)
