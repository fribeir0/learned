import nmap
import json
import requests
from datetime import datetime
import socket

# Define o alvo da rede
alvo = '192.168.0.0/24'

# Webhook do n8n (substitua com o seu)
webhook_url = 'https://n8n.srv794951.hstgr.cloud/webhook-test/b1098a7e-6f0f-4ee4-bd14-ddbdfbcf91fe'

# Inicializa scanner
nm = nmap.PortScanner()

# Faz o scan
print(f"🔍 Escaneando a rede {alvo}...")
nm.scan(hosts=alvo, arguments='-O -sS')

# Cria lista de resultados
resultado = []
scan_id = f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

for host in nm.all_hosts():
    host_info = {
        'scan_id': scan_id,
        'host': host,
        'status': nm[host].state(),
        'hostname': socket.getfqdn(host),
        'timestamp': datetime.utcnow().isoformat(),
        'os': nm[host]['osmatch'][0]['name'] if nm[host].has_tcp(80) and nm[host].has_key('osmatch') and nm[host]['osmatch'] else 'Desconhecido',
        'portas_abertas': []
    }

    for proto in nm[host].all_protocols():
        portas = nm[host][proto].keys()
        for porta in portas:
            host_info['portas_abertas'].append({
                'porta': porta,
                'protocolo': proto,
                'servico': nm[host][proto][porta]['name'],
                'estado': nm[host][proto][porta]['state']
            })

    resultado.append(host_info)

# Envia para o n8n
print(f"🚀 Enviando {len(resultado)} dispositivos para o n8n...")
resposta = requests.post(webhook_url, json=resultado)

if resposta.ok:
    print("✅ Dados enviados com sucesso!")
else:
    print("❌ Falha ao enviar:", resposta.status_code, resposta.text)
