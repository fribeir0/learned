# Traffic Shaver no pfSense

Este repositório documenta a configuração do **Traffic Shaver** no pfSense para otimizar e controlar o tráfego de rede.

## O que é Traffic Shaver?
O **Traffic Shaver** é uma funcionalidade do pfSense utilizada para aplicar regras de controle de largura de banda. Ele faz parte do **QoS (Quality of Service)**, permitindo priorizar e limitar o tráfego de rede com base em diferentes critérios.

### Benefícios do Traffic Shaver:
- **Controle de tráfego**: Define prioridades para diferentes tipos de conexão.
- **Gerenciamento de largura de banda por protocolo**: Limita a velocidade de protocolos específicos.
- **Restrição por usuário ou IP**: Define limites personalizados para cada dispositivo.
- **Otimização de VoIP**: Garante qualidade para chamadas de voz sobre IP.
- **Bloqueio de tráfego não essencial**: Reduz consumo desnecessário de banda.

## Como configurar o Traffic Shaver no pfSense

### Criando um Limiter
1. Acesse **Firewall > Traffic Shaper > Limiters**.
2. Clique em **New Limiter**.
3. Marque a opção **Enable** para ativar o limitador.
4. Defina a largura de banda máxima permitida.
5. Salve as configurações.

### Aplicando o Limitador a uma Regra
1. Acesse **Firewall > Rules**.
2. Selecione a regra onde deseja aplicar o limitador.
3. No menu **Extra > Advanced**, configure os valores de **IN/OUT Pipe**.
4. Selecione os **Shaves** configurados anteriormente.
5. Salve e aplique as configurações.

Com isso, o Traffic Shaver estará configurado para otimizar o uso da rede e garantir uma distribuição eficiente da largura de banda.

