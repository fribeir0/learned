from scapy.all import ARP, Ether, srp, conf, ICMP, IP, sr1, TCP
import socket
import concurrent.futures
from datetime import datetime
import logging
import netifaces
import time
import requests
from typing import Dict, List, Callable, Optional, Tuple

class AdvancedNetworkScanner:
    def __init__(self):
        self.devices = []
        self._stop_flag = False
        self._progress_callback = None
        self._current_scan_start = None
        self.mac_vendor_cache = {}
        
        # Configurações ajustáveis
        self.timeouts = {
            'arp': 2,
            'port': 0.3,
            'icmp': 1,
            'service': 1.5
        }
        
        self.max_workers = 50
        self.max_arp_retries = 1
        
        # Portas comuns para varredura rápida
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
            993, 995, 1723, 3306, 3389, 5900, 8080, 8443
        ]
        
        # Configuração do Scapy
        conf.verb = 0
        conf.retry = 1
        conf.timeout = 1000
        
        # Configuração de logging
        self.logger = logging.getLogger('AdvancedNetworkScanner')
        self.logger.setLevel(logging.INFO)

    def reset(self):
        self.devices = []
        self._stop_flag = False
        self._current_scan_start = None

    def stop_scan(self):
        self._stop_flag = True
        self.logger.info("Scan stopped by user")

    def _get_vendor_from_api(self, mac: str) -> Optional[str]:
        try:
            oui = mac.replace(':', '').upper()[:6]
            if oui in self.mac_vendor_cache:
                return self.mac_vendor_cache[oui]
            
            url = f"https://api.macvendors.com/{oui}"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                vendor = response.text.strip()
                self.mac_vendor_cache[oui] = vendor
                return vendor
            return None
        except:
            return None

    def _get_vendor(self, mac: str) -> str:
        vendor = self._get_vendor_from_api(mac)
        if vendor:
            return vendor
            
        prefix = ':'.join(mac.split(':')[:3]).lower()
        vendors = {
            '00:00:0c': 'Cisco',
            '00:0d:4b': 'Netgear',
            '00:16:3e': 'Xen',
            '00:1a:11': 'Dell',
            '00:1c:c4': 'HP',
            'b8:27:eb': 'Raspberry Pi',
            '08:00:27': 'VirtualBox'
        }
        return vendors.get(prefix, 'Unknown')

    def _check_port(self, ip: str, port: int, timeout: float = None) -> Tuple[int, bool]:
        if timeout is None:
            timeout = self.timeouts['port']
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return (port, s.connect_ex((ip, port)) == 0)
        except:
            return (port, False)

    def _get_ttl(self, ip: str) -> Optional[int]:
        """Obtém o TTL do host via ICMP ping"""
        try:
            packet = IP(dst=ip)/ICMP()
            response = sr1(packet, timeout=self.timeouts['icmp'], verbose=False)
            return response.ttl if response else None
        except:
            return None

    def _full_port_scan(self, ip: str, scan_type: str = 'common') -> Dict[str, List[int]]:
        if self._stop_flag:
            return {'open': [], 'filtered': []}
            
        # Define portas a serem escaneadas
        if scan_type == 'all':
            ports = list(range(1, 65536))
            timeout = 0.1
            workers = min(100, len(ports))
        else:
            ports = self.common_ports
            timeout = self.timeouts['port']
            workers = self.max_workers
            
        open_ports = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self._check_port, ip, port, timeout): port for port in ports}
            
            for future in concurrent.futures.as_completed(futures):
                if self._stop_flag:
                    break
                    
                port, is_open = future.result()
                if is_open:
                    open_ports.append(port)
                    if self._progress_callback:
                        self._progress_callback({
                            'type': 'port_open',
                            'ip': ip,
                            'port': port
                        })
        
        return {'open': sorted(open_ports)}

    def _get_default_network(self) -> Optional[str]:
        """Obtém a rede padrão automaticamente"""
        try:
            for iface in netifaces.interfaces():
                if iface == 'lo':
                    continue
                    
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        if 'addr' in addr_info and 'netmask' in addr_info:
                            ip = addr_info['addr']
                            if ip != '127.0.0.1':
                                network = '.'.join(ip.split('.')[:3] + ['0'])
                                return f"{network}/24"
        except:
            return None

    def scan_network(self, network: str = None, scan_type: str = 'common', callback: Callable = None) -> bool:
        self.reset()
        self._current_scan_start = time.time()
        self._progress_callback = callback
        
        try:
            if network is None:
                network = self._get_default_network()
                if network is None:
                    self.logger.error("Could not determine network automatically")
                    return False
                    
            if '/' not in network:
                network += '.0/24'
                
            self.logger.info(f"Starting {scan_type} scan on network: {network}")
            
            # Fase 1: Descoberta ARP
            ans, _ = srp(
                Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network),
                timeout=self.timeouts['arp'],
                retry=self.max_arp_retries,
                verbose=False
            )
            
            # Fase 2: Processamento paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for _, rcv in ans:
                    if self._stop_flag:
                        break
                        
                    ip = rcv.psrc
                    mac = rcv.hwsrc
                    
                    futures.append(
                        executor.submit(self._process_device, ip, mac, scan_type)
                    )
                    
                for future in concurrent.futures.as_completed(futures):
                    if self._stop_flag:
                        break
                        
            scan_time = time.time() - self._current_scan_start
            self.logger.info(f"Scan completed in {scan_time:.2f} seconds. Found {len(self.devices)} devices.")
            
            return not self._stop_flag
            
        except Exception as e:
            self.logger.error(f"Scan error: {e}")
            return False

    def _process_device(self, ip: str, mac: str, scan_type: str):
        if self._stop_flag:
            return
            
        try:
            ttl = self._get_ttl(ip)
            vendor = self._get_vendor(mac)
            ports_result = self._full_port_scan(ip, scan_type)
            
            device = {
                'ip': ip,
                'mac': mac,
                'vendor': vendor,
                'open_ports': ports_result['open'],
                'status': 'online' if ports_result['open'] else 'offline',
                'last_seen': datetime.now().isoformat(),
                'ttl': ttl
            }
            
            self.devices.append(device)
            
            if self._progress_callback:
                self._progress_callback({
                    'type': 'device_update',
                    'device': device
                })
                
        except Exception as e:
            self.logger.error(f"Error processing device {ip}: {e}")

    def get_results(self) -> Dict:
        return {
            'devices': sorted(self.devices, key=lambda x: [int(i) for i in x['ip'].split('.')]),
            'scan_time': datetime.now().isoformat()
        }

# Alias para manter compatibilidade
NetworkScanner = AdvancedNetworkScanner