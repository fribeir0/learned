
## Configuração de Redundância de Gateway no pfSense

### Passos para configurar:
1. Adicione uma nova WAN.
2. Acesse **System > Routing**.
3. Em **Gateways Group**, clique em **Add**.
4. Selecione as duas WANs.
5. Defina **Prioridade Tier 1** para ambas.
6. Configure os **Triggers**:
   - **Member Down**: Se um cair, o outro assume.
   - **Packet Loss**: Se houver perda de pacotes, o outro assume.
   - **High Latency**: Se houver alta latência, o outro assume.

### Configuração do Gateway Padrão
1. Volte para **Routing**.
2. Em **Gateway**, defina o **Default Gateway IPv4** como o grupo criado.
3. Repita o processo para IPv6, se necessário.

Com essa configuração, o pfSense garantirá alta disponibilidade para conexões de internet.

