from scapy.all import *
import sys
import time
import os
from threading import Thread, Semaphore
from queue import Queue
from ipaddress import ip_network

# Configurações
MAX_HOST_THREADS = 20      # Threads para descobrir hosts
MAX_PORT_THREADS = 50      # Threads para escanear portas
PING_TIMEOUT = 1           # Timeout para ping
PORT_SCAN_TIMEOUT = 2      # Timeout para scan de portas
print_lock = Semaphore(value=1)  # Para evitar sobreposição de saída

def is_admin():
    """Verifica se o programa está sendo executado como administrador"""
    try:
        # Para Windows
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        # Para Unix/Linux
        else:
            return os.geteuid() == 0
    except:
        return False

def ping_sweep(network):
    """Descobre hosts ativos na rede usando ICMP echo request (ping)"""
    active_hosts = []
    network = ip_network(network, strict=False)
    
    def ping_host(ip):
        try:
            pkt = IP(dst=str(ip))/ICMP()
            resp = sr1(pkt, timeout=PING_TIMEOUT, verbose=0)
            if resp:
                with print_lock:
                    print(f"[+] Host ativo: {ip}")
                active_hosts.append(str(ip))
        except:
            pass
    
    threads = []
    for ip in network.hosts():
        if str(ip) == network.broadcast_address:
            continue
        t = Thread(target=ping_host, args=(ip,))
        t.start()
        threads.append(t)
        
        while len(threads) >= MAX_HOST_THREADS:
            for t in threads[:]:
                if not t.is_alive():
                    threads.remove(t)
    
    for t in threads:
        t.join()
    
    return active_hosts

def port_scan(target_ip, port, results):
    """Função que executa o scan individual de uma porta"""
    try:
        pkt = IP(dst=target_ip)/TCP(dport=port, flags="S")
        response = sr1(pkt, timeout=PORT_SCAN_TIMEOUT, verbose=0)
        
        if response is None:
            return
        elif response.haslayer(TCP):
            if response[TCP].flags == 0x12:  # SYN-ACK (porta aberta)
                send_rst = IP(dst=target_ip)/TCP(dport=port, flags="R")
                send(send_rst, verbose=0)
                with print_lock:
                    print(f"[+] {target_ip}:{port} - ABERTA")
                results.append(port)
    except Exception as e:
        with print_lock:
            print(f"[!] Erro ao escanear {target_ip}:{port}: {str(e)}", file=sys.stderr)

def threaded_port_scan(target_ip, ports):
    """Escaneia todas as portas em um host usando threads"""
    port_queue = Queue()
    results = []
    
    for port in ports:
        port_queue.put(port)
    
    threads = []
    for _ in range(min(MAX_PORT_THREADS, len(ports))):
        t = Thread(target=lambda: [port_scan(target_ip, port_queue.get(), results) for _ in iter(int, 1)])
        t.daemon = True
        t.start()
        threads.append(t)
    
    port_queue.join()
    return results

def parse_ports(port_input):
    """Analisa a entrada do usuário e retorna lista de portas"""
    ports = []
    try:
        if '-' in port_input:
            start, end = map(int, port_input.split('-'))
            ports = list(range(start, end+1))
        elif ',' in port_input:
            ports = list(map(int, port_input.split(',')))
        else:
            ports = [int(port_input)]
        
        for port in ports:
            if not 0 < port < 65536:
                raise ValueError(f"Porta inválida: {port}")
        return ports
    except ValueError as e:
        print(f"Erro no formato das portas: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    try:
        print("=== Scanner de Rede /24 ===")
        
        if not is_admin():
            print("Este script requer privilégios administrativos.", file=sys.stderr)
            print("Por favor, execute como Administrador.", file=sys.stderr)
            sys.exit(1)
        
        network = input("Digite a rede (ex: 192.168.1.0/24): ").strip()
        if not network.endswith('/24'):
            print("Aviso: Você deve escanear uma rede /24", file=sys.stderr)
            if '/' in network:
                print("Convertendo para /24...")
                network = network.split('/')[0] + '/24'
            else:
                network += '/24'
        
        port_input = input("Digite as portas (ex: 80 ou 1-100 ou 22,80,443): ").strip()
        ports = parse_ports(port_input)
        
        print(f"\nIniciando scan na rede {network}...")
        start_time = time.time()
        
        print("\n[Fase 1] Descobrindo hosts ativos...")
        active_hosts = ping_sweep(network)
        
        if not active_hosts:
            print("Nenhum host ativo encontrado.")
            return
        
        print(f"\n[Fase 2] Escaneando portas nos {len(active_hosts)} hosts ativos...")
        print(f"Portas alvo: {ports}\n")
        
        scan_results = {}
        for host in active_hosts:
            print(f"\nEscaneando {host}...")
            open_ports = threaded_port_scan(host, ports)
            if open_ports:
                scan_results[host] = sorted(open_ports)
        
        print("\n=== RESULTADOS FINAIS ===")
        print(f"Tempo total: {time.time() - start_time:.2f} segundos")
        
        if scan_results:
            print("\nHosts com portas abertas:")
            for host, ports in scan_results.items():
                print(f"{host}: {', '.join(map(str, ports))}")
        else:
            print("Nenhuma porta aberta encontrada na rede.")
            
    except KeyboardInterrupt:
        print("\nScan interrompido pelo usuário.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()