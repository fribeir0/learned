# Configurando um Proxy com SquidGuard no pfSense

Este repositório documenta a configuração do **SquidGuard** no pfSense para bloquear URLs e domínios, utilizando ou não listas de bloqueio (blacklist).

## O que é SquidGuard?
O **SquidGuard** é um complemento para o proxy **Squid**, permitindo o bloqueio de sites com base em URLs, domínios e categorias de blacklist. Ele é utilizado para controle de acesso e segurança na rede.

### Benefícios do SquidGuard:
- **Bloqueio de sites por URL ou domínio**.
- **Uso de listas de bloqueio (blacklists)**.
- **Filtro de conteúdo baseado em categorias**.
- **Controle de acesso personalizável**.

## Como configurar o SquidGuard no pfSense

### Instalando e Habilitando o SquidGuard
1. Acesse **System > Package Manager**.
2. Instale os pacotes **Squid** e **SquidGuard**.
3. Acesse **Services > SquidGuard Proxy Filter**.
4. Habilite a opção **Enable SquidGuard** e salve.

### Criando uma Regra de Bloqueio Manual
1. Acesse a aba **Common ACL**.
2. Em **Target Rules List**, clique em **Add**.
3. Defina um nome para a regra (ex.: bloqueio_rede_social).
4. No campo **Domains**, adicione os domínios a serem bloqueados (ex.: facebook.com, youtube.com).
5. No campo **URLs**, insira URLs específicas se necessário.
6. Escolha **Deny** como ação de bloqueio e salve.

### Utilizando Blacklists
1. Acesse a aba **Blacklist**.
2. No campo **Blacklist URL**, insira o link para uma lista de bloqueio confiável (ex.: Shallalist, UT1 Blacklist).
3. Clique em **Download** e depois **Apply**.
4. Retorne à aba **Common ACL** e aplique as blacklists nas regras desejadas.

### Aplicando as Configurações
1. Clique em **Apply** para ativar as regras.
2. Reinicie o serviço **SquidGuard** para garantir que as regras entrem em vigor.

Com essas configurações, o SquidGuard estará bloqueando os sites definidos manualmente ou os incluídos na blacklist.

