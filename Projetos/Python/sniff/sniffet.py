from scapy.all import sniff, Ether, ARP
from scapy.layers.inet import IP

def packet_callback(packet):
    if packet.haslayer(IP):
        org= {packet[IP].src}
        dst = {packet[IP].dst}

        if dst == "192.168.0.255":
            print(f"Origem:{packet[IP].src} Destino: {packet[IP].dst}")

def packetEther (packet):
    if packet.haslayer(Ether):
        org = packet[Ether].src
        dst = packet[Ether].dst
        if dst.lower() == "ff:ff:ff:ff:ff:ff":
            print (f"BROADCAST Origem:{org} Destino: {dst}")
            if packet.haslayer(ARP):
                arpOrg= packet[ARP].psrc
                arpDst= packet[ARP].pdst
                print (f"ARP Quem e? :{arpDst}, quem perguntou foi o: {arpOrg}")
sniff(prn=packetEther)