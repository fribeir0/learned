from scapy.all import *
def scan (ip,ports):
    p = IP(dst=ip) / TCP(dport=ports, flags="S")

    ans, uns= sr(p, timeout=2, retry=1,verbose=0)
    result = []

    for sent, received in ans:
        if received.haslayer(TCP) and received[TCP].flags == 0x12:
            result.append(received[TCP].sport)
            print("passou")
        else:
            print(f"Dispositivo recusou conexao na porta: {ports}")

    return result
    

if __name__ == "__main__":
    add = input("Coloque o ip ou a rede a ser escaneada")
    port = int(input("Coloque as portas"))
    scan(add,port)