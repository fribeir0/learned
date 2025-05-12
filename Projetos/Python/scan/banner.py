import socket

def banner_grab_http(ip, port=80):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, port))

        # Enviando requisição HTTP simples
        request = f"GET / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())

        # Recebendo resposta (banner HTTP)
        response = s.recv(1024)
        print(f"Banner HTTP de {ip}:{port}:\n")
        print(response.decode(errors='ignore'))

        s.close()

    except Exception as e:
        print(f"Erro ao conectar em {ip}:{port} -> {e}")

# Exemplo de uso
banner_grab_http("172.16.43.254", 80)
