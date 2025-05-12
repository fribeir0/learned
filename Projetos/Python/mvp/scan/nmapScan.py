import nmap
import json

def run_nmap_scan(network_range):
    nm = nmap.PortScanner()

    # Defina os parâmetros do Nmap de acordo com a necessidade.
    arguments = "-T4 -sS -p 1-1000"
    nm.scan(hosts=network_range, arguments=arguments)
    
    hosts = []

    for host in nm.all_hosts():
        if nm[host].state() == "up":
            host_data = {
                "ip": host,
                "hostname": nm[host].hostname() if nm[host].hostname() else "Unknown",
                "ports": [],
                "services": []
            }

            for proto in nm[host].all_protocols():
                ports = nm[host][proto].keys()
                for port in ports:
                    service = nm[host][proto][port]
                    service_data = {
                        "name": service.get("name", "Unknown"),
                        "product": service.get("product", "Unknown"),
                        "version": service.get("version", "Unknown")
                    }
                    host_data["ports"].append(port)
                    host_data["services"].append(service_data)
            
            hosts.append(host_data)

    # Converte os dados para JSON e retorna
    return json.dumps(hosts, indent=4)

# Exemplo de uso
network_range = "192.168.1.0/24"
scan_result = run_nmap_scan(network_range)
print(scan_result)
