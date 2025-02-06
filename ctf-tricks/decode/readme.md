# Cracking de Hashes para CTF

Este documento cobre o uso do John the Ripper, Hashcat e ferramentas nativas do Linux para decodificação de hashes.

## Instalação
### John the Ripper
```bash
sudo apt update && sudo apt install john
```

### Hashcat
```bash
sudo apt update && sudo apt install hashcat
```

## Identificação do Tipo de Hash
Antes de quebrar uma hash, é importante identificar seu tipo:
```bash
hashid 22060c294de035a32bbb2b6308901860
```
Ou, usando Hashcat:
```bash
hashcat --example-hashes | grep "22060c294de035a32bbb2b6308901860"
```

## Uso do John the Ripper
### Converter Hash para Formato Compatível
```bash
john --show --format=raw-md5 hash.txt
```

### Ataque de Dicionário
```bash
echo "22060c294de035a32bbb2b6308901860" > hash.txt
john --wordlist=rockyou.txt --format=raw-md5 hash.txt
```

### Ataque de Força Bruta
```bash
john --incremental=All --format=raw-md5 hash.txt
```

## Uso do Hashcat
### Ataque de Dicionário
```bash
echo "22060c294de035a32bbb2b6308901860" > hash.txt
hashcat -m 0 -a 0 hash.txt rockyou.txt
```

### Ataque de Força Bruta
```bash
hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a
```

### Recuperar Sessão Interrompida
```bash
hashcat --session=hashcat --restore
```

## Decodificação de Strings no Linux
O Linux possui ferramentas nativas para decodificação de algumas codificações comuns:

### Base64
```bash
echo "c2VuaGE=" | base64 -d
```

### ROT13
```bash
echo "uryyb jbeyq" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

### URL Encode/Decode
```bash
echo "%7Btest%7D" | python3 -c "import sys, urllib.parse; print(urllib.parse.unquote(sys.stdin.read().strip()))"
```

### Hexadecimal
```bash
echo "68656c6c6f" | xxd -r -p
```

### MD5/SHA1/SHA256
Calcular hashes:
```bash
echo -n "senha123" | md5sum
echo -n "senha123" | sha1sum
echo -n "senha123" | sha256sum
```

## Observações
- Utilize apenas em ambientes autorizados.
- Sempre verifique os Termos de Serviço antes de testar senhas.
- Ferramentas como Hashcat e John the Ripper podem consumir muitos recursos, use com cuidado.

