# Comandos Git Essenciais 🛠️

Este guia reúne os comandos Git mais úteis que utilizo no meu dia a dia para gerenciar repositórios e versionamento de código. Cada comando é explicado de forma clara e prática.

---

## 🔍 Comandos Básicos

### Verificar Versão do Git
```bash
git -v
Verifica a versão instalada do Git. 
```
### Ajuda e Documentação

```bash
git help -a
git --help
Exibe a lista completa de comandos ou a documentação oficial do Git.
```
## Inicializar um Repositório

```bash
git init
Inicializa um novo repositório Git na pasta atual.
```
## Configurar Usuário

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
Define o nome e e-mail globais para os commits.
```
## 📂 Gerenciamento de Arquivos
Adicionar Arquivos ao Stage
```bash
git add <arquivo>
Adiciona um arquivo específico ao stage (área de preparação) para commit.
```
##Remover Arquivos
```bash
git rm <arquivo>
Remove um arquivo do repositório e o marca como excluído no próximo commit.
```
##Mover ou Renomear Arquivos
```bash
git mv <arquivo>
Move ou renomeia um arquivo e atualiza o repositório.
```
##💾 Commits e Histórico
Verificar Histórico de Commits
```bash
git log
Exibe o histórico de commits com detalhes como autor, data e mensagem.
```
##Fazer um Commit
```bash
git commit -m "Mensagem do commit"
Registra as alterações no repositório com uma mensagem descritiva.
Observação: Para fazer um commit, os arquivos precisam estar no stage (usando git add).
```
#Reverter Commits
```bash
git revert HEAD
Reverte o último commit.
```
```bash
git revert HEAD~2
Reverte o commit de duas posições atrás do HEAD.
```
```bash
git revert <hash-do-commit>
Reverte um commit específico pelo seu hash.
```
##🔄 Sincronização com Repositórios Remotos
Enviar Alterações para o Repositório Remoto
```bash
git push
Envia as alterações do repositório local para o remoto.
```
##Atualizar Repositório Local
```bash
git pull
Atualiza o repositório local com as alterações do repositório remoto.
```
##🌿 Branches (Ramificações)
Criar uma Nova Branch
```bash
git branch <nome-da-branch>
Cria uma nova branch para trabalhar em uma funcionalidade específica.
```
##Listar Todas as Branches
```bash
git branch
Lista todas as branches do repositório.
```
##Alternar entre Branches
```bash
Copy
git checkout <nome-da-branch>
Muda para a branch especificada.
```
##Mesclar Branches
```bash
Copy
git merge <nome-da-branch>
Combina as alterações de uma branch com a branch atual (geralmente a main ou master).
```
##Atualizar uma Branch com Rebase
```bash
Copy
git rebase master
Atualiza a branch atual com as alterações da branch master.
```
##🛠️ Comandos Adicionais
Verificar Status do Repositório
```bash
Copy
git status
Exibe o estado atual do repositório (arquivos modificados, em stage, etc.).
```
##Clonar um Repositório
```bash
Copy
git clone <url-do-repositorio>
Cria uma cópia local de um repositório remoto.
```
##📜 Licença
Este guia está licenciado sob a MIT License. Sinta-se à vontade para usar e compartilhar!
