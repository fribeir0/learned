from flask import Flask, render_template
import socket
from scapy.all import ARP, Ether, srp, IP, ICMP, sr1
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)

# Função para checar as portas abertas
def check_remote(ip, ports):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Timeout de 1 segundo
                result = s.connect_ex((ip, port))  # Tenta conectar
                if result == 0:
                    open_ports.append(port)  # Porta aberta
        except socket.timeout:
            pass
    return open_ports

# Função para escanear dispositivos na rede
def scan_devices(target):
    broadcast = "ff:ff:ff:ff:ff:ff"
    packet_arp = ARP(pdst=target)
    packet_ether = Ether(dst=broadcast)
    packet = packet_ether / packet_arp
    result, _ = srp(packet, timeout=1, verbose=False)
    
    devices = []
    for sent, received in result:
        device_info = {"ip": received.psrc, "mac": received.hwsrc}
        devices.append(device_info)
    
    return devices

# Função para realizar o escaneamento e enviar os resultados
def generate_scan_output(network):
    devices = []
    with ThreadPoolExecutor(max_workers=10) as executor:  # Limite de threads para 10
        targets = [f"{network}.{i}" for i in range(1, 255)]
        results = executor.map(scan_devices, targets)
        
        for result in results:
            for device in result:
                try:
                    # Verifica se o dispositivo está ativo com um pacote ICMP
                    pacote_icmp = IP(dst=device["ip"]) / ICMP()
                    result_icmp = sr1(pacote_icmp, timeout=1, verbose=False)
                    device['status'] = 'Ativo' if result_icmp else 'Inativo'
                    device['os'] = 'Windows' if result_icmp and result_icmp[IP].ttl > 64 else 'Linux'
                    ports = [22, 3389]
                    device['open_ports'] = check_remote(device["ip"], ports)
                except Exception as e:
                    print(f"Erro ao escanear dispositivo {device['ip']}: {e}")
                    device['status'] = 'Erro'
                    device['os'] = 'Desconhecido'
                    device['open_ports'] = []
                
                devices.append(device)

    # Contagem final
    total_devices = len(devices)
    windows_count = sum(1 for device in devices if device['os'] == 'Windows')
    linux_count = sum(1 for device in devices if device['os'] == 'Linux')
    open_ports_count = sum(1 for device in devices if device['open_ports'])

    return devices, total_devices, windows_count, linux_count, open_ports_count

# Rota do Flask para realizar o scan e exibir os resultados
@app.route("/scan")
def scan_network():
    network = "192.168.0"  # Substitua pelo valor da sua rede
    devices, total_devices, windows_count, linux_count, open_ports_count = generate_scan_output(network)
    return render_template(
        "scan_template.html",
        network=network,
        devices=devices,
        total_devices=total_devices,
        windows_count=windows_count,
        linux_count=linux_count,
        open_ports_count=open_ports_count
    )

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
