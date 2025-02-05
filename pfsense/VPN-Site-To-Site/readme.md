# VPN com IPsec Client-to-Site no pfSense

Este repositório documenta a configuração de uma VPN IPsec no pfSense, incluindo tanto a fase 1 quanto a fase 2.

## O que é VPN?
Uma VPN (Virtual Private Network) cria um túnel virtual criptografado para a transmissão segura de dados entre redes.

### Tipos de VPN:
- **Site-to-Site**: Conecta redes diferentes (ex.: matriz com filial).
- **Client-to-Site**: Permite que um usuário remoto se conecte à rede como se estivesse fisicamente presente.

## IPsec (Internet Protocol Security)
Protocolo de segurança que opera na camada 3 do modelo OSI. Seus componentes principais são:
- **AH (Authentication Header)**: Autentica sem criptografar.
- **ESP (Encapsulating Security Payload)**: Autentica e criptografa.
- **IKE (Internet Key Exchange)**: Gerencia a troca de chaves para estabelecer a VPN.

### Modos de funcionamento:
- **Modo Transporte**: Apenas o payload é criptografado.
- **Modo Túnel**: Todo o pacote é encapsulado e criptografado.

## Configuração da VPN no pfSense

### Fase 1 (Configuração do túnel e troca de chaves)
1. Acesse **VPN > IPsec** no pfSense.
2. Clique em **Add P1**.
3. Escolha **IKEv2** como versão do IKE.
4. Defina o **Remote Gateway** como o IP da WAN do destino.
5. Configure uma **PreShared Key** (chave compartilhada).

### Fase 2 (Definição das redes locais e remotas)
1. No mesmo menu, clique em **Show Phase2 Entry** e depois em **Add P2**.
2. Selecione o **Mode** como **Tunnel**.
3. Em **Remote Network**, defina a LAN remota (ex.: 192.168.19.0/24).
4. Em **Local Network**, defina a LAN local (ex.: 192.168.5.0/24).
5. Selecione **ESP** para criptografar todo o pacote.
6. Escolha **SHA-256** como algoritmo de integridade.

### Configuração de Regras
1. Acesse **Firewall > Rules > IPsec**.
2. Adicione uma regra **Any/Any** para permitir o tráfego entre as redes conectadas via VPN.

Com isso, a VPN estará configurada e funcional no pfSense.

