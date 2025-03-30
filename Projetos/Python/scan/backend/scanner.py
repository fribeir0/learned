from scapy.all import ARP, Ether, srp, conf, ICMP, IP, sr1
import socket
import concurrent.futures
from datetime import datetime
import logging
import netifaces
import time
from typing import Dict, List, Callable, Optional

class NetworkScanner:
    def __init__(self):
        self.devices = []
        self._stop_flag = False
        self._progress_callback = None
        self._current_scan_start = None
        
        # Configurações ajustáveis
        self.timeouts = {
            'arp': 2,
            'port': 0.5,
            'icmp': 1,
            'service': 1.5
        }
        
        self.max_workers = 20  # Threads para varredura de portas
        self.max_arp_retries = 1
        
        # Banco de dados de fabricantes (exemplo reduzido)
        self.mac_vendors = {
            '00:00:0c': 'Cisco',
            '00:0d:4b': 'Netgear',
            '00:16:3e': 'Xen',
            '00:1a:11': 'Dell',
            '00:1c:c4': 'HP',
            '00:24:8c': 'Dell',
            '00:26:b9': 'Microsoft',
            '00:50:f2': 'Microsoft',
            '00:15:5d': 'Microsoft Hyper-V',
            '00:03:93': 'Apple',
            '00:1c:b3': 'Apple',
            '00:25:bc': 'Apple',
            'b8:27:eb': 'Raspberry Pi',
            'dc:a6:32': 'Raspberry Pi',
            'e4:5f:01': 'Espressif',
            '08:00:27': 'VirtualBox',
            '00:1b:21': 'Huawei',
            '00:23:15': 'TP-Link',
            '00:26:18': 'Samsung'
        }
        
        # Configuração do Scapy
        conf.verb = 0
        conf.retry = 1
        conf.timeout = 1000  # em ms
        
        # Configuração de logging
        self.logger = logging.getLogger('NetworkScanner')
        self.logger.setLevel(logging.INFO)
        
    def reset(self):
        """Reseta o scanner para um novo scan"""
        self.devices = []
        self._stop_flag = False
        self._current_scan_start = None
        
    def stop_scan(self):
        """Para o scan em andamento"""
        self._stop_flag = True
        self.logger.info("Scan stopped by user")
        
    def set_progress_callback(self, callback: Callable):
        """Define um callback para progresso"""
        self._progress_callback = callback
        
    def _get_vendor(self, mac: str) -> str:
        """Obtém o fabricante do dispositivo pelo MAC"""
        try:
            prefix = ':'.join(mac.split(':')[:3]).lower()
            return self.mac_vendors.get(prefix, 'Unknown')
        except:
            return 'Unknown'
            
    def _check_port(self, ip: str, port: int, timeout: float = None) -> bool:
        """Verificação robusta de porta"""
        if timeout is None:
            timeout = self.timeouts['port']
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\0'*8)
                return s.connect_ex((ip, port)) == 0
        except:
            return False
            
    def _check_icmp(self, ip: str) -> bool:
        """Verifica se o host responde a ping"""
        try:
            packet = IP(dst=ip)/ICMP()
            response = sr1(packet, timeout=self.timeouts['icmp'], verbose=False)
            return response is not None
        except:
            return False
            
    def _get_ttl(self, ip: str) -> Optional[int]:
        """Obtém o TTL do host"""
        try:
            packet = IP(dst=ip)/ICMP()
            response = sr1(packet, timeout=self.timeouts['icmp'], verbose=False)
            return response.ttl if response else None
        except:
            return None
            
    def _parallel_port_scan(self, ip: str) -> Dict[str, List[int]]:
        """Varredura paralela de portas otimizada"""
        if self._stop_flag:
            return {'OS': [], 'Services': []}
            
        # Portas prioritárias para detecção rápida
        priority_ports = {
            'Windows': [445, 3389, 135, 139],
            'Linux': [22, 111, 631],
            'MacOS': [22, 445, 548],
            'Router': [80, 443, 23],
            'IoT': [1883, 5683, 80]
        }
        
        # Todas as portas únicas para verificação
        all_ports = list({port for ports in priority_ports.values() for port in ports})
        
        open_ports = []
        
        # Usando ThreadPool para verificação paralela
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(all_ports), self.max_workers)) as executor:
            futures = {executor.submit(self._check_port, ip, port): port for port in all_ports}
            
            for future in concurrent.futures.as_completed(futures):
                if self._stop_flag:
                    break
                    
                port = futures[future]
                try:
                    if future.result():
                        open_ports.append(port)
                except:
                    continue
                    
        return {'OS': open_ports, 'Services': open_ports}
        
    def _detect_os(self, ip: str, mac: str, open_ports: List[int], ttl: Optional[int]) -> str:
        """Detecção inteligente de sistema operacional"""
        vendor = self._get_vendor(mac).lower()
        
        # 1. Verificação por prefixo MAC
        if 'apple' in vendor:
            return 'MacOS'
        elif 'microsoft' in vendor or 'hyper-v' in vendor:
            return 'Windows'
        elif 'raspberry' in vendor or 'espressif' in vendor:
            return 'IoT'
        elif any(x in vendor for x in ['cisco', 'aruba', 'tp-link', 'netgear', 'huawei']):
            return 'Router'
            
        # 2. Verificação por portas abertas
        port_matches = {
            'Windows': any(p in open_ports for p in [445, 3389, 135, 139]),
            'Linux': any(p in open_ports for p in [22, 111, 631]),
            'MacOS': any(p in open_ports for p in [548, 5900]),
            'Router': any(p in open_ports for p in [80, 443, 23, 8080]),
            'IoT': any(p in open_ports for p in [1883, 5683, 8080])
        }
        
        for os_type, matches in port_matches.items():
            if matches:
                return os_type
                
        # 3. Fallback para TTL
        if ttl is not None:
            if 120 <= ttl <= 128:
                return 'Windows'
            elif 60 <= ttl <= 64:
                return 'Linux' if 22 in open_ports else 'Unknown'
            elif ttl >= 250:
                return 'Router'
                
        return 'Unknown'
        
    def _get_default_network(self) -> Optional[str]:
        """Tenta determinar a rede padrão automaticamente"""
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
            
    def scan_network(self, network: str = None, callback: Callable = None) -> bool:
        """
        Executa o scan de rede com tratamento robusto de erros
        
        Args:
            network: Rede no formato '192.168.1.0/24' ou '192.168.1'
            callback: Função para receber atualizações em tempo real
            
        Returns:
            bool: True se o scan foi completado com sucesso
        """
        self.reset()
        self._current_scan_start = time.time()
        
        try:
            # Determina a rede a ser escaneada
            if network is None:
                network = self._get_default_network()
                if network is None:
                    self.logger.error("Não foi possível determinar a rede automaticamente")
                    return False
                    
            # Padroniza o formato da rede
            if '/' not in network:
                if network.count('.') == 3:
                    network = network.rstrip('.0') + '.0/24'
                else:
                    network += '.0/24'
                    
            self.logger.info(f"Iniciando scan na rede: {network}")
            
            # Fase 1: Descoberta ARP
            try:
                ans, _ = srp(
                    Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network),
                    timeout=self.timeouts['arp'],
                    retry=self.max_arp_retries,
                    verbose=False,
                    iface_hint=network
                )
            except Exception as e:
                self.logger.error(f"Falha no scan ARP: {e}")
                return False
                
            # Fase 2: Processamento paralelo dos hosts
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for _, rcv in ans:
                    if self._stop_flag:
                        break
                        
                    ip = rcv.psrc
                    mac = rcv.hwsrc
                    
                    futures.append(
                        executor.submit(self._process_device, ip, mac, callback)
                    )
                    
                # Aguarda a conclusão ou interrupção
                for future in concurrent.futures.as_completed(futures):
                    if self._stop_flag:
                        break
                        
            scan_time = time.time() - self._current_scan_start
            self.logger.info(f"Scan completado em {scan_time:.2f} segundos. {len(self.devices)} dispositivos encontrados.")
            
            return not self._stop_flag
            
        except KeyboardInterrupt:
            self.logger.info("Scan interrompido pelo usuário")
            return False
        except Exception as e:
            self.logger.error(f"Erro crítico durante o scan: {e}")
            return False
            
    def _process_device(self, ip: str, mac: str, callback: Callable = None):
        """Processa um dispositivo em paralelo"""
        if self._stop_flag:
            return
            
        try:
            # Obtém informações básicas
            ttl = self._get_ttl(ip)
            vendor = self._get_vendor(mac)
            
            # Varredura de portas
            port_scan_result = self._parallel_port_scan(ip)
            open_ports = port_scan_result['OS']
            
            # Detecção de OS
            os_type = self._detect_os(ip, mac, open_ports, ttl)
            
            # Verificação de status
            is_online = len(open_ports) > 0 or self._check_icmp(ip)
            
            # Monta o dispositivo
            device = {
                'ip': ip,
                'mac': mac,
                'os': os_type,
                'vendor': vendor,
                'ports': open_ports,
                'status': 'online' if is_online else 'no response',
                'last_seen': datetime.now().isoformat(),
                'ttl': ttl
            }
            
            self.devices.append(device)
            
            # Notifica o callback se fornecido
            if callback:
                callback({
                    'device': device,
                    'summary': self._get_summary()
                })
                
        except Exception as e:
            self.logger.error(f"Erro ao processar dispositivo {ip}: {e}")
            
    def _get_summary(self) -> Dict:
        """Gera um resumo dos resultados"""
        os_counts = {
            'Windows': 0,
            'Linux': 0,
            'MacOS': 0,
            'Router': 0,
            'IoT': 0,
            'Unknown': 0
        }
        
        for device in self.devices:
            os_counts[device['os']] = os_counts.get(device['os'], 0) + 1
            
        return {
            'total_devices': len(self.devices),
            'os_counts': os_counts,
            'scan_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def get_results(self) -> Dict:
        """Retorna os resultados formatados"""
        return {
            'devices': sorted(self.devices, key=lambda x: [int(i) for i in x['ip'].split('.')]),
            'summary': self._get_summary()
        }