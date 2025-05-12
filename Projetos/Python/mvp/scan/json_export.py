import json
import datetime
import requests
from config import output_json, n8n_webhook

def save_results(network_range, hosts_data):
    result = {
        "scan_time": datetime.datetime.utcnow().isoformat(),
        "network_range": network_range,
        "hosts": hosts_data
    }

    with open(output_json, "w") as f:
        json.dump(result, f, indent=2)
    return result

def send_to_n8n(json_data):
    try:
        response = requests.post(n8n_webhook, json=json_data)
        print(f"[→] Enviado para n8n: {response.status_code}")
    except Exception as e:
        print(f"[!] Erro ao enviar para n8n: {e}")
