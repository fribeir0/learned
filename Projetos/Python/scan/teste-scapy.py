import socket
import requests
import urllib3
from scapy.all import ARP, Ether, srp, IP, ICMP, sr1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor

hc = 0
linux_count = 0
microsoft_count = 0
unknown_count = 0
network=input(f"Qual rede voce deseja escanear? (siga o exemplo a seguir) \n192.168.0\n")


def scan_devices(target):
    broadcast = "ff:ff:ff:ff:ff:ff"
    packet_arp = ARP(pdst=target)
    packet_ether = Ether(dst=broadcast)
    packet = packet_ether / packet_arp
    

    result, _ = srp(packet, timeout=1, verbose=False)
    
    for sent, received in result:
        device_info = {"ip": received.psrc, "mac": received.hwsrc}
        yield device_info 

def scan(network):
    global hc, linux_count, microsoft_count, unknown_count
    answer=int (input("Deseja realizar um scan de portas SSH e RDP?\n 1- SIM\n 2- NAO\n"))
    if answer <= 2:
        with ThreadPoolExecutor(max_workers=20) as executor: 
            targets = [f"{network}.{i}" for i in range(1, 255)]
            

            results = executor.map(scan_devices, targets)
            
        
            for result in results:
                for device in result:
                    print(f"Dispositivo encontrado - IP: {device['ip']}, MAC: {device['mac']}")
                    pacote_icmp= IP(dst=device["ip"]) / ICMP()
                    result_icmp= sr1(pacote_icmp, timeout=1, verbose=False)
                    
                    if result_icmp :
                        endpoint = True
                        hc += 1
                        print (f"Host Ativo ")
                        print (f"TTL Do endpoint e: {result_icmp[IP].ttl}")
                        ttl = result_icmp[IP].ttl
                        if 120 <= ttl <= 128:
                            endpoint_so="Windows"
                            print (f"Windows TTL")
                            microsoft_count += 1
                        if 60 <= ttl <= 64:
                            endpoint_so="Linux"
                            print (f"Linux TTL")
                            linux_count += 1
                        if 250 >= ttl <= 255:
                            endpoint_so="Cisco"
                            print(f"Cisco TTL")
                    else :
                        print (f"Inativo ou ICMP bloquado")
                        endpoint = False
                        unknown_count += 1

                    if answer == 1:
                        ports = {22,3389,80,443,21,25,143,53,3306}
                        open_ports = check_remote(device["ip"],ports)
                        if open_ports:
                            print (f"Portas Abertas em dispositivo: {device['ip']} {open_ports}")
                            
                        else :
                            print (f"Nenhuma porta aberta")


def check_remote(ip, ports):
    opens = []

    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5) 
            result = s.connect_ex((ip, port))

            if result == 0:
                opens.append(port)
                print(f"Porta {port} aberta no IP {ip}")

                try:
                    s.settimeout(1)
                    banner = s.recv(1024).decode(errors='ignore').strip()
                    if banner:
                        print(f" Detalhes ocultos ({port}): {banner}")

                except socket.timeout:
                    print(f"Porta {port} aberta, mas sem resposta (timeout)")

                    # Tentar CURL HTTP/HTTPS
                    if port in [80, 443, 8080, 8443]:  
                        try:
                            url = f"http://{ip}:{port}" if port in [80, 8080] else f"https://{ip}:{port}"
                            response = requests.get(url, timeout=2, verify=False)  # Ignora SSL inválido
                            print(f"Resposta HTTP {port}: {response.status_code} - {response.reason}")
                            print(f"Cabeçalhos: {response.headers}")
                        except requests.exceptions.RequestException as e:
                            print(f"Erro ao tentar curl na porta {port}: {e}")
                except Exception as e:
                    print(f"Erro ao ler banner na porta {port}: {e}")

    return opens
scan(network)
print (f"Host Ativos: {hc}")
print (f"Linux: {linux_count}")
print (f"Microsoft: {microsoft_count}")
print (f"Desconhecidos: {unknown_count}")

