import socket
from scapy.all import ARP, Ether, srp, IP, ICMP, sr1

from concurrent.futures import ThreadPoolExecutor

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
    answer=int (input("Deseja realizar um scan de portas SSH e RDP?\n 1- SIM\n2- NAO"))
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
                    print (f"Host Ativo ")
                    print (f"TTL Do endpoint e: {result_icmp[IP].ttl}")
                    ttl = result_icmp[IP].ttl
                    if ttl > 64 :
                        endpoint_so="Windows"
                        print (f"Windows TTL")
                    else :
                        endpoint_so="Linux"
                        print (f"Linux TTL")
                else :
                    print (f"Inativo ou ICMP bloquado")
                    endpoint = False

                if answer == 1:
                    ports = {22,3389}
                    open_ports = check_remote(device["ip"],ports)
                    if open_ports:
                        print (f"Portas Abertas em dispositivo: {device['ip']} {open_ports}")
                        
                    else :
                        print (f"Nenhuma porta aberta")


def check_remote (ip, ports):
    opens = []

    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip,port))

            if result == 0:
                remote=True
                opens.append(port)
                banner = s.recv(1024).decode().strip()
                print (f"Detalhes ocultos: {banner}")
    return opens

network = "192.168.0"
scan(network)
