import socket
from scapy.all import ARP, Ether, srp, IP, ICMP, sr1
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os

class NetworkScanner:
    def __init__(self):
        """Inicializa o scanner com valores padrão"""
        self.hc = 0  # Contador de hosts ativos
        self.linux_count = 0  # Contador de sistemas Linux
        self.microsoft_count = 0  # Contador de sistemas Windows
        self.unknown_count = 0  # Contador de sistemas desconhecidos
        self.devices = []  # Lista de dispositivos encontrados
        self.scan_time = None  # Timestamp do scan
        self.update_callback = None  # Callback para atualizações em tempo real
        self._stop_scan = False  # Flag para parar o scan

    def reset(self):
        """Reinicia todos os contadores e listas"""
        self.hc = 0
        self.linux_count = 0
        self.microsoft_count = 0
        self.unknown_count = 0
        self.devices = []
        self.scan_time = None
        self._stop_scan = False

    def stop_scan(self):
        """Para o scan em andamento"""
        self._stop_scan = True

    def set_update_callback(self, callback):
        """Define a função de callback para atualizações em tempo real"""
        self.update_callback = callback

    def scan_devices(self, target):
        """Escaneia dispositivos em um único endereço IP"""
        try:
            if self._stop_scan:
                return []

            broadcast = "ff:ff:ff:ff:ff:ff"
            packet_arp = ARP(pdst=target)
            packet_ether = Ether(dst=broadcast)
            packet = packet_ether / packet_arp
            
            # Envia pacote ARP e captura respostas
            result, _ = srp(packet, timeout=1, verbose=False, iface=None)
            
            devices = []
            for sent, received in result:
                if self._stop_scan:
                    break
                    
                device_info = {
                    "ip": received.psrc, 
                    "mac": received.hwsrc, 
                    "os": "Unknown", 
                    "ports": [],
                    "status": "online"
                }
                devices.append(device_info)
            
            return devices
        except Exception as e:
            print(f"Erro ao escanear {target}: {e}")
            return []

    def check_ports(self, ip, ports):
        """Verifica portas abertas em um IP específico"""
        if self._stop_scan:
            return []

        open_ports = []
        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    if s.connect_ex((ip, port)) == 0:
                        open_ports.append(port)
                        try:
                            banner = s.recv(1024).decode().strip()
                            if banner:
                                print(f"Banner na porta {port}: {banner}")
                        except:
                            pass
            except:
                pass
        return open_ports

    def detect_os(self, ttl):
        """Detecta o sistema operacional baseado no TTL"""
        if ttl > 64:
            self.microsoft_count += 1
            return "Windows"
        else:
            self.linux_count += 1
            return "Linux"

    def scan_network(self, network, scan_ports=False):
        """Escaneia toda uma rede"""
        self.reset()
        ports = {22, 3389} if scan_ports else set()
        
        try:
            with ThreadPoolExecutor(max_workers=20) as executor:
                # Cria lista de IPs para escanear
                targets = [f"{network}.{i}" for i in range(1, 255)]
                
                # Escaneia os dispositivos em paralelo
                results = executor.map(self.scan_devices, targets)
                
                for result in results:
                    if self._stop_scan:
                        break
                        
                    for device in result:
                        if self._stop_scan:
                            break
                            
                        try:
                            # Verifica se o host responde a ICMP
                            pacote_icmp = IP(dst=device["ip"]) / ICMP()
                            result_icmp = sr1(pacote_icmp, timeout=1, verbose=False)
                            
                            if result_icmp:
                                self.hc += 1
                                ttl = result_icmp[IP].ttl
                                device["os"] = self.detect_os(ttl)
                            else:
                                self.unknown_count += 1
                                device["status"] = "no-icmp"
                            
                            # Verifica portas se solicitado
                            if scan_ports and not self._stop_scan:
                                device["ports"] = self.check_ports(device["ip"], ports)
                            
                            self.devices.append(device)
                            
                            # Notifica atualização via callback
                            if self.update_callback and not self._stop_scan:
                                self.update_callback({
                                    'device': device,
                                    'summary': {
                                        'total_devices': self.hc,
                                        'linux_count': self.linux_count,
                                        'windows_count': self.microsoft_count,
                                        'unknown_count': self.unknown_count
                                    }
                                })
                                
                        except Exception as e:
                            print(f"Erro ao processar dispositivo {device.get('ip', '?')}: {e}")
                            continue
        except Exception as e:
            print(f"Erro no scan_network: {e}")
            raise
        
        self.scan_time = datetime.now().isoformat()
        return not self._stop_scan  # Retorna True se o scan foi completado

    def get_results(self):
        """Retorna os resultados do scan em formato JSON"""
        return {
            "summary": {
                "total_devices": self.hc,
                "linux_count": self.linux_count,
                "windows_count": self.microsoft_count,
                "unknown_count": self.unknown_count,
                "scan_time": self.scan_time
            },
            "devices": self.devices
        }

    def save_to_json(self, filename="scan_results.json"):
        """Salva os resultados em um arquivo JSON"""
        with open(filename, "w") as f:
            json.dump(self.get_results(), f, indent=2)