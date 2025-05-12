package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"text/template"
	"time"

	"github.com/gin-gonic/gin"
)

// Configuração da aplicação
type Config struct {
	N8NWebhookURL  string   `json:"n8n_webhook_url"`
	TargetDomains  []string `json:"target_domains"`
	TargetIPs      []string `json:"target_ips"`
	ScanDepth      string   `json:"scan_depth"`
	OutputDir      string   `json:"output_dir"`
	PDToolsEnabled []string `json:"pd_tools_enabled"`
}

// Resultados de scan
type ScanResult struct {
	ToolName    string    `json:"tool_name"`
	Command     string    `json:"command"`
	StartTime   time.Time `json:"start_time"`
	EndTime     time.Time `json:"end_time"`
	Duration    string    `json:"duration"`
	Output      string    `json:"output"`
	ErrorOutput string    `json:"error_output"`
	Success     bool      `json:"success"`
	TargetInfo  string    `json:"target_info"`
}

// Estrutura da análise completa
type FullScanReport struct {
	CompanyName  string       `json:"company_name"`
	ScanDate     time.Time    `json:"scan_date"`
	ScanResults  []ScanResult `json:"scan_results"`
	Summary      string       `json:"summary"`
	TotalTargets int          `json:"total_targets"`
	ScanDuration string       `json:"scan_duration"`
	Config       Config       `json:"config"`
}

// Templates HTML
const indexHTML = `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise de Vulnerabilidades</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Analisador de Vulnerabilidades</h1>
        </header>
        <main>
            <div class="scan-form">
                <h2>Nova Análise</h2>
                <form id="scanForm">
                    <div class="form-group">
                        <label for="companyName">Nome da Empresa:</label>
                        <input type="text" id="companyName" name="companyName" required>
                    </div>
                    <div class="form-group">
                        <label for="n8nWebhookURL">URL do Webhook N8N:</label>
                        <input type="url" id="n8nWebhookURL" name="n8nWebhookURL" required 
                           placeholder="https://seu-servidor-n8n.com/webhook/xxxx">
                    </div>
                    <div class="form-group">
                        <label for="targetDomains">Domínios Alvo (um por linha):</label>
                        <textarea id="targetDomains" name="targetDomains" rows="4" 
                          placeholder="exemplo.com.br
subdominio.exemplo.com.br"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="targetIPs">IPs Alvo (um por linha):</label>
                        <textarea id="targetIPs" name="targetIPs" rows="4" 
                          placeholder="192.168.1.1
10.0.0.0/24"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="scanDepth">Profundidade da Análise:</label>
                        <select id="scanDepth" name="scanDepth">
                            <option value="basic">Básica (rápida)</option>
                            <option value="standard" selected>Padrão (recomendada)</option>
                            <option value="deep">Profunda (demorada)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Ferramentas do Project Discovery:</label>
                        <div class="checkbox-group">
                            <label><input type="checkbox" name="pdTools" value="nuclei" checked> Nuclei</label>
                            <label><input type="checkbox" name="pdTools" value="subfinder" checked> Subfinder</label>
                            <label><input type="checkbox" name="pdTools" value="httpx" checked> HTTPX</label>
                            <label><input type="checkbox" name="pdTools" value="naabu" checked> Naabu</label>
                        </div>
                    </div>
                    <div class="form-group buttons">
                        <button type="submit" id="startScan">Iniciar Análise</button>
                        <button type="reset">Limpar</button>
                    </div>
                </form>
            </div>
            
            <div id="scanProgress" class="scan-progress hidden">
                <h2>Progresso da Análise</h2>
                <div class="progress-bar">
                    <div class="progress" id="progressBar"></div>
                </div>
                <p id="progressStatus">Preparando...</p>
                <div id="logOutput" class="log-output"></div>
            </div>
            
            <div id="scanResults" class="scan-results hidden">
                <h2>Resultados da Análise</h2>
                <div id="resultSummary"></div>
                <div class="buttons">
                    <button id="viewDetailedResults">Ver Resultados Detalhados</button>
                    <button id="downloadReport">Baixar Relatório</button>
                </div>
            </div>
        </main>
        <footer>
            <p>&copy; 2025 Analisador de Vulnerabilidades</p>
        </footer>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>
`

const styleCSS = `
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --bg-color: #f8f9fa;
    --text-color: #333;
    --success-color: #2ecc71;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: var(--primary-color);
    color: white;
    padding: 20px;
    text-align: center;
    border-radius: 8px 8px 0 0;
    margin-bottom: 30px;
}

h1 {
    margin: 0;
    font-size: 2.2rem;
}

h2 {
    color: var(--primary-color);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--secondary-color);
}

.scan-form, .scan-progress, .scan-results {
    background-color: white;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

.form-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
}

input[type="text"],
input[type="url"],
textarea,
select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

textarea {
    resize: vertical;
}

.checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
}

.checkbox-group label {
    display: flex;
    align-items: center;
    font-weight: normal;
}

.checkbox-group input[type="checkbox"] {
    margin-right: 8px;
}

button {
    background-color: var(--secondary-color);
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #2980b9;
}

button[type="reset"] {
    background-color: #95a5a6;
}

button[type="reset"]:hover {
    background-color: #7f8c8d;
}

.buttons {
    display: flex;
    gap: 10px;
    justify-content: flex-start;
}

/* Progress Bar */
.progress-bar {
    background-color: #ecf0f1;
    border-radius: 4px;
    height: 25px;
    margin-bottom: 20px;
    overflow: hidden;
}

.progress {
    background-color: var(--secondary-color);
    height: 100%;
    width: 0;
    transition: width 0.3s ease;
}

.log-output {
    background-color: #2c3e50;
    color: #ecf0f1;
    padding: 15px;
    border-radius: 4px;
    font-family: monospace;
    height: 300px;
    overflow-y: auto;
    margin-top: 20px;
}

.hidden {
    display: none;
}

/* Success/Error Messages */
.success {
    color: var(--success-color);
    font-weight: bold;
}

.error {
    color: var(--danger-color);
    font-weight: bold;
}

.warning {
    color: var(--warning-color);
    font-weight: bold;
}

footer {
    text-align: center;
    padding: 20px;
    color: #7f8c8d;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .scan-form, .scan-progress, .scan-results {
        padding: 15px;
    }
    
    h1 {
        font-size: 1.8rem;
    }
    
    .checkbox-group {
        grid-template-columns: 1fr;
    }
}
`

const mainJS = `
document.addEventListener('DOMContentLoaded', function() {
    const scanForm = document.getElementById('scanForm');
    const scanProgress = document.getElementById('scanProgress');
    const scanResults = document.getElementById('scanResults');
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');
    const logOutput = document.getElementById('logOutput');
    const viewDetailedResults = document.getElementById('viewDetailedResults');
    const downloadReport = document.getElementById('downloadReport');
    
    let scanId = '';
    
    scanForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validar form
        const companyName = document.getElementById('companyName').value;
        const n8nWebhookURL = document.getElementById('n8nWebhookURL').value;
        const targetDomains = document.getElementById('targetDomains').value;
        const targetIPs = document.getElementById('targetIPs').value;
        
        if (!companyName || !n8nWebhookURL || (!targetDomains && !targetIPs)) {
            alert('Por favor, preencha os campos obrigatórios.');
            return;
        }
        
        // Coletar dados do formulário
        const pdToolsChecked = Array.from(document.querySelectorAll('input[name="pdTools"]:checked'))
            .map(checkbox => checkbox.value);
            
        const scanData = {
            company_name: companyName,
            config: {
                n8n_webhook_url: n8nWebhookURL,
                target_domains: targetDomains.split('\\n').filter(line => line.trim()),
                target_ips: targetIPs.split('\\n').filter(line => line.trim()),
                scan_depth: document.getElementById('scanDepth').value,
                pd_tools_enabled: pdToolsChecked,
                output_dir: ""  // Será preenchido pelo backend
            }
        };
        
        // Iniciar scan
        fetch('/api/scan/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(scanData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                scanId = data.scan_id;
                scanForm.classList.add('hidden');
                scanProgress.classList.remove('hidden');
                startProgressMonitoring(scanId);
                addLogMessage('Análise iniciada. ID: ' + scanId);
            } else {
                alert('Erro ao iniciar análise: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao iniciar análise. Verifique o console para mais detalhes.');
        });
    });
    
    function startProgressMonitoring(id) {
        const eventSource = new EventSource('/api/scan/progress/' + id);
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            // Atualizar barra de progresso
            progressBar.style.width = data.progress_percent + '%';
            
            // Atualizar status
            progressStatus.textContent = data.status_message;
            
            // Adicionar logs
            if (data.log_message) {
                addLogMessage(data.log_message);
            }
            
            // Verificar se o scan terminou
            if (data.completed) {
                eventSource.close();
                progressStatus.textContent = 'Análise concluída!';
                scanResults.classList.remove('hidden');
                updateResultSummary(data.summary);
            }
        };
        
        eventSource.onerror = function() {
            eventSource.close();
            addLogMessage('Erro na conexão com o servidor. Tentando reconectar...', 'error');
            setTimeout(() => startProgressMonitoring(id), 5000);
        };
    }
    
    function addLogMessage(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const msgElement = document.createElement('div');
        msgElement.className = type;
        msgElement.textContent = `[${timestamp}] ${message}`;
        logOutput.appendChild(msgElement);
        
        // Auto-scroll para o final
        logOutput.scrollTop = logOutput.scrollHeight;
    }
    
    function updateResultSummary(summary) {
        const resultSummary = document.getElementById('resultSummary');
        resultSummary.innerHTML = summary;
    }
    
    viewDetailedResults.addEventListener('click', function() {
        window.open('/results/' + scanId, '_blank');
    });
    
    downloadReport.addEventListener('click', function() {
        window.location.href = '/api/scan/download/' + scanId;
    });
});
`

const resultsHTML = `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultados Detalhados - {{.CompanyName}}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        .results-container {
            background-color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .result-section {
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 20px;
        }
        
        .result-section:last-child {
            border-bottom: none;
        }
        
        .tool-name {
            background-color: #2c3e50;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .tool-name .duration {
            font-weight: normal;
            font-size: 0.9em;
        }
        
        .command {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            overflow-x: auto;
            font-family: monospace;
        }
        
        .output-container {
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .output-tabs {
            display: flex;
            background-color: #f5f5f5;
            border-bottom: 1px solid #ddd;
        }
        
        .output-tab {
            padding: 10px 15px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .output-tab.active {
            background-color: #3498db;
            color: white;
        }
        
        .output-content {
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
            font-family: monospace;
            white-space: pre-wrap;
        }
        
        .summary-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .summary-item {
            margin-bottom: 10px;
        }
        
        .nav-tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        
        .nav-tab {
            padding: 10px 20px;
            cursor: pointer;
            border: 1px solid transparent;
            border-bottom: none;
            margin-right: 5px;
            border-radius: 8px 8px 0 0;
            transition: all 0.3s;
        }
        
        .nav-tab:hover {
            background-color: #f5f5f5;
        }
        
        .nav-tab.active {
            background-color: white;
            border-color: #ddd;
            border-bottom-color: white;
            margin-bottom: -1px;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .vuln-entry {
            background-color: #fff;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .vuln-high {
            border-left-color: #e74c3c;
        }
        
        .vuln-medium {
            border-left-color: #f39c12;
        }
        
        .vuln-low {
            border-left-color: #3498db;
        }
        
        .vuln-info {
            border-left-color: #7f8c8d;
        }
        
        .vuln-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .vuln-title {
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .vuln-severity {
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 0.9em;
            color: white;
        }
        
        .severity-high {
            background-color: #e74c3c;
        }
        
        .severity-medium {
            background-color: #f39c12;
        }
        
        .severity-low {
            background-color: #3498db;
        }
        
        .severity-info {
            background-color: #7f8c8d;
        }
        
        .vuln-details {
            margin-top: 10px;
        }
        
        .back-btn {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Análise de Vulnerabilidades - {{.CompanyName}}</h1>
        </header>
        
        <button class="back-btn" onclick="window.location.href='/'">← Voltar</button>
        
        <div class="summary-section">
            <h2>Resumo da Análise</h2>
            <div class="summary-item"><strong>Empresa:</strong> {{.CompanyName}}</div>
            <div class="summary-item"><strong>Data da análise:</strong> {{.ScanDate.Format "02/01/2006 15:04:05"}}</div>
            <div class="summary-item"><strong>Duração total:</strong> {{.ScanDuration}}</div>
            <div class="summary-item"><strong>Total de alvos analisados:</strong> {{.TotalTargets}}</div>
        </div>
        
        <div class="nav-tabs">
            <div class="nav-tab active" data-tab="overview">Visão Geral</div>
            <div class="nav-tab" data-tab="vulnerabilities">Vulnerabilidades</div>
            <div class="nav-tab" data-tab="detailedResults">Resultados Detalhados</div>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="results-container">
                <h2>Visão Geral das Descobertas</h2>
                <div id="overviewContent">
                    {{.Summary}}
                </div>
            </div>
        </div>
        
        <div id="vulnerabilities" class="tab-content">
            <div class="results-container">
                <h2>Vulnerabilidades Encontradas</h2>
                <div id="vulnFilters">
                    <button class="filter-btn active" data-severity="all">Todas</button>
                    <button class="filter-btn" data-severity="high">Alta</button>
                    <button class="filter-btn" data-severity="medium">Média</button>
                    <button class="filter-btn" data-severity="low">Baixa</button>
                    <button class="filter-btn" data-severity="info">Informativa</button>
                </div>
                <div id="vulnList">
                    <!-- Vulnerabilidades serão inseridas via JavaScript -->
                </div>
            </div>
        </div>
        
        <div id="detailedResults" class="tab-content">
            <div class="results-container">
                <h2>Resultados Detalhados por Ferramenta</h2>
                
                {{range .ScanResults}}
                <div class="result-section">
                    <div class="tool-name">
                        <span>{{.ToolName}}</span>
                        <span class="duration">Duração: {{.Duration}}</span>
                    </div>
                    
                    <div class="command">$ {{.Command}}</div>
                    
                    <div class="output-container">
                        <div class="output-tabs">
                            <div class="output-tab active" data-output="{{.ToolName}}-output">Saída</div>
                            {{if .ErrorOutput}}
                            <div class="output-tab" data-output="{{.ToolName}}-error">Erros</div>
                            {{end}}
                        </div>
                        
                        <div id="{{.ToolName}}-output" class="output-content active">{{.Output}}</div>
                        {{if .ErrorOutput}}
                        <div id="{{.ToolName}}-error" class="output-content">{{.ErrorOutput}}</div>
                        {{end}}
                    </div>
                </div>
                {{end}}
            </div>
        </div>
        
        <footer>
            <p>&copy; 2025 Analisador de Vulnerabilidades</p>
        </footer>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Tab navigation
            const navTabs = document.querySelectorAll('.nav-tab');
            const tabContents = document.querySelectorAll('.tab-content');
            
            navTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    // Remove active class from all tabs
                    navTabs.forEach(t => t.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));
                    
                    // Add active class to current tab
                    this.classList.add('active');
                    document.getElementById(this.dataset.tab).classList.add('active');
                });
            });
            
            // Output tabs
            document.querySelectorAll('.output-tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    // Get parent container
                    const container = this.closest('.output-container');
                    
                    // Remove active class from all tabs in this container
                    container.querySelectorAll('.output-tab').forEach(t => t.classList.remove('active'));
                    container.querySelectorAll('.output-content').forEach(c => c.classList.remove('active'));
                    
                    // Add active class to current tab
                    this.classList.add('active');
                    container.querySelector('#' + this.dataset.output).classList.add('active');
                });
            });
            
            // Carregar vulnerabilidades
            fetch('/api/scan/vulnerabilities/{{.ScanID}}')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderVulnerabilities(data.vulnerabilities);
                    } else {
                        document.getElementById('vulnList').innerHTML = '<p>Erro ao carregar vulnerabilidades: ' + data.error + '</p>';
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    document.getElementById('vulnList').innerHTML = '<p>Erro ao carregar vulnerabilidades.</p>';
                });
                
            function renderVulnerabilities(vulnerabilities) {
                const vulnList = document.getElementById('vulnList');
                vulnList.innerHTML = '';
                
                if (vulnerabilities.length === 0) {
                    vulnList.innerHTML = '<p>Nenhuma vulnerabilidade encontrada.</p>';
                    return;
                }
                
                vulnerabilities.forEach(vuln => {
                    const vulnEl = document.createElement('div');
                    vulnEl.className = 'vuln-entry vuln-' + vuln.severity.toLowerCase();
                    vulnEl.dataset.severity = vuln.severity.toLowerCase();
                    
                    const html = `
                        <div class="vuln-header">
                            <div class="vuln-title">${vuln.title}</div>
                            <div class="vuln-severity severity-${vuln.severity.toLowerCase()}">${vuln.severity}</div>
                        </div>
                        <div class="vuln-target">${vuln.target}</div>
                        <div class="vuln-details">
                            <p>${vuln.description}</p>
                            ${vuln.recommendation ? '<p><strong>Recomendação:</strong> ' + vuln.recommendation + '</p>' : ''}
                        </div>
                    `;
                    
                    vulnEl.innerHTML = html;
                    vulnList.appendChild(vulnEl);
                });
                
                // Filtros de vulnerabilidade
                document.querySelectorAll('#vulnFilters .filter-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        document.querySelectorAll('#vulnFilters .filter-btn').forEach(b => b.classList.remove('active'));
                        this.classList.add('active');
                        
                        const severity = this.dataset.severity;
                        document.querySelectorAll('.vuln-entry').forEach(entry => {
                            if (severity === 'all' || entry.dataset.severity === severity) {
                                entry.style.display = 'block';
                            } else {
                                entry.style.display = 'none';
                            }
                        });
                    });
                });
            }
        });
    </script>
</body>
</html>
`

// Função principal
func main() {
	// Flags para configuração
	var port string
	var outputDir string
	var debug bool

	flag.StringVar(&port, "port", "8080", "Porta para executar o servidor")
	flag.StringVar(&outputDir, "output", "./scans", "Diretório para armazenar resultados das análises")
	flag.BoolVar(&debug, "debug", false, "Ativar modo de depuração")
	flag.Parse()

	// Criar diretório de saída se não existir
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Erro ao criar diretório de saída: %v", err)
	}

	// Criar diretório para arquivos estáticos
	createStaticFiles(outputDir)

	// Verificar ferramentas instaladas
	checkRequiredTools()

	// Configurar router Gin
	router := setup