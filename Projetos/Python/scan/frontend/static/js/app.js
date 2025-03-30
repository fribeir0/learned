document.addEventListener('DOMContentLoaded', function() {
    // Elementos da UI
    const loadingElement = document.getElementById('loading');
    const statusMessage = document.getElementById('status-message');
    const scanButton = document.getElementById('scanButton');
    const stopButton = document.getElementById('stopButton');
    const exportBtn = document.getElementById('export-btn');
    const searchInput = document.getElementById('search');
    const devicesTable = document.getElementById('devicesTable').getElementsByTagName('tbody')[0];
    const themeCheckbox = document.getElementById('theme-checkbox');
    const themeLabel = document.getElementById('theme-label');
    const networkRangeInput = document.getElementById('network-range');
    
    // Elementos de contagem
    const linuxCount = document.getElementById('linux-count');
    const windowsCount = document.getElementById('windows-count');
    const routerCount = document.getElementById('router-count');
    const iotCount = document.getElementById('iot-count');
    const unknownCount = document.getElementById('unknown-count');
    
    // Estado da aplicação
    let isScanning = false;
    let devices = [];
    let socket = null;
    let currentScanId = null;
    
    // Inicialização
    init();
    
    function init() {
        setupEventListeners();
        connectSocket();
        loadThemePreference();
    }
    
    function setupEventListeners() {
        scanButton.addEventListener('click', startScan);
        stopButton.addEventListener('click', stopScan);
        exportBtn.addEventListener('click', exportToCSV);
        searchInput.addEventListener('input', filterDevices);
        themeCheckbox.addEventListener('change', toggleTheme);
        
        // Lidar com atualização de página/aba fechando
        window.addEventListener('beforeunload', handleBeforeUnload);
    }
    
    function connectSocket() {
        if (socket) {
            socket.disconnect();
        }
        
        // Configuração robusta do Socket.IO
        socket = io({
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            timeout: 20000,
            transports: ['websocket', 'polling']
        });
        
        socket.on('connect', () => {
            console.log('Conectado ao servidor');
            statusMessage.textContent = 'Pronto para escanear';
            updateUIAfterConnection(true);
        });
        
        socket.on('disconnect', (reason) => {
            console.log('Desconectado do servidor:', reason);
            if (isScanning) {
                statusMessage.textContent = 'Conexão perdida durante o escaneamento';
            }
            updateUIAfterConnection(false);
        });
        
        socket.on('connect_error', (error) => {
            console.error('Erro de conexão:', error);
            statusMessage.textContent = 'Erro de conexão com o servidor';
            updateUIAfterConnection(false);
            
            // Tentar reconectar após 5 segundos
            setTimeout(connectSocket, 5000);
        });
        
        socket.on('connection_response', (data) => {
            console.log('Resposta de conexão:', data);
            currentScanId = data.client_id;
        });
        
        socket.on('scan_update', handleScanUpdate);
    }
    
    function updateUIAfterConnection(connected) {
        scanButton.disabled = !connected;
        if (!connected) {
            stopButton.disabled = true;
            loadingElement.classList.add('hidden');
            isScanning = false;
        }
    }
    
    function handleScanUpdate(data) {
        console.log('Atualização de escaneamento:', data);
        
        switch(data.type) {
            case 'progress':
                if (!devices.some(d => d.ip === data.data.device.ip)) {
                    devices.push(data.data.device);
                    updateDevicesTable();
                    updateSummary(data.data.summary);
                }
                break;
                
            case 'complete':
                completeScan();
                if (data.data && data.data.devices) {
                    devices = data.data.devices;
                    updateDevicesTable();
                    updateSummary(data.data.summary);
                }
                break;
                
            case 'status':
                statusMessage.textContent = data.message;
                break;
                
            case 'error':
                handleScanError(data.message);
                break;
        }
    }
    
    function startScan() {
        if (isScanning) return;
        
        isScanning = true;
        devices = [];
        devicesTable.innerHTML = '';
        resetCounters();
        
        loadingElement.classList.remove('hidden');
        scanButton.disabled = true;
        stopButton.disabled = false;
        statusMessage.textContent = 'Iniciando escaneamento...';
        
        const networkRange = networkRangeInput.value.trim();
        
        if (!isValidNetworkRange(networkRange)) {
            handleScanError('Intervalo de rede inválido. Use o formato "192.168.0"');
            return;
        }
        
        if (socket && socket.connected) {
            socket.emit('start_scan', { 
                network: networkRange 
            }, (response) => {
                if (response && response.error) {
                    handleScanError(response.error);
                }
            });
        } else {
            handleScanError('Não conectado ao servidor. Tentando reconectar...');
            connectSocket();
        }
    }
    
    function isValidNetworkRange(range) {
        const parts = range.split('.');
        if (parts.length !== 3) return false;
        
        return parts.every(part => {
            const num = parseInt(part, 10);
            return !isNaN(num) && num >= 0 && num <= 255;
        });
    }
    
    function stopScan() {
        if (!isScanning) return;
        
        if (socket && socket.connected) {
            socket.emit('stop_scan');
            statusMessage.textContent = 'Parando escaneamento...';
        }
    }
    
    function completeScan() {
        isScanning = false;
        loadingElement.classList.add('hidden');
        scanButton.disabled = false;
        stopButton.disabled = true;
        statusMessage.textContent = `Escaneamento completo! ${devices.length} dispositivos encontrados`;
    }
    
    function handleScanError(message) {
        console.error('Erro no escaneamento:', message);
        statusMessage.textContent = 'Erro: ' + message;
        loadingElement.classList.add('hidden');
        scanButton.disabled = false;
        stopButton.disabled = true;
        isScanning = false;
    }
    
    function updateDevicesTable() {
        devicesTable.innerHTML = '';
        
        devices.sort((a, b) => {
            const ipA = a.ip.split('.').map(part => parseInt(part, 10));
            const ipB = b.ip.split('.').map(part => parseInt(part, 10));
            
            for (let i = 0; i < 4; i++) {
                if (ipA[i] !== ipB[i]) {
                    return ipA[i] - ipB[i];
                }
            }
            return 0;
        });
        
        devices.forEach(device => {
            const row = devicesTable.insertRow();
            
            // Status
            let statusClass = 'status-offline';
            let statusText = 'Offline';
            
            if (device.status === 'online') {
                statusClass = 'status-online';
                statusText = 'Online';
            }
            
            // OS class
            let osClass = '';
            if (device.os && device.os.includes('Linux')) osClass = 'os-linux';
            else if (device.os && device.os.includes('Windows')) osClass = 'os-windows';
            else if (device.os && device.os.includes('Router')) osClass = 'os-router';
            else if (device.os && device.os.includes('IoT')) osClass = 'os-iot';
            
            // Portas
            let portsText = 'None';
            if (device.ports && device.ports.length > 0) {
                portsText = device.ports.join(', ');
                if (portsText.length > 30) {
                    portsText = device.ports.slice(0, 3).join(', ') + '...';
                }
            }
            
            row.innerHTML = `
                <td>${device.ip || 'Unknown'}</td>
                <td>${device.mac || 'Unknown'}</td>
                <td class="${osClass}">${device.os || 'Unknown'}</td>
                <td>${device.vendor || 'Unknown'}</td>
                <td title="${device.ports ? device.ports.join(', ') : ''}">${portsText}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            `;
        });
    }
    
    function updateSummary(summary) {
        if (!summary) return;
        
        linuxCount.textContent = summary.os_counts?.Linux || 0;
        windowsCount.textContent = summary.os_counts?.Windows || 0;
        routerCount.textContent = summary.os_counts?.Router || 0;
        iotCount.textContent = summary.os_counts?.IoT || 0;
        unknownCount.textContent = summary.os_counts?.Unknown || 0;
    }
    
    function resetCounters() {
        linuxCount.textContent = '0';
        windowsCount.textContent = '0';
        routerCount.textContent = '0';
        iotCount.textContent = '0';
        unknownCount.textContent = '0';
    }
    
    function filterDevices() {
        const searchTerm = searchInput.value.toLowerCase();
        
        if (!searchTerm) {
            updateDevicesTable();
            return;
        }
        
        const filtered = devices.filter(device => 
            (device.ip && device.ip.toLowerCase().includes(searchTerm)) ||
            (device.mac && device.mac.toLowerCase().includes(searchTerm)) ||
            (device.vendor && device.vendor.toLowerCase().includes(searchTerm)) ||
            (device.os && device.os.toLowerCase().includes(searchTerm)) ||
            (device.ports && device.ports.some(port => port.toString().includes(searchTerm)))
        );
        
        devicesTable.innerHTML = '';
        
        filtered.forEach(device => {
            const row = devicesTable.insertRow();
            
            let statusClass = 'status-offline';
            let statusText = 'Offline';
            
            if (device.status === 'online') {
                statusClass = 'status-online';
                statusText = 'Online';
            }
            
            let osClass = '';
            if (device.os && device.os.includes('Linux')) osClass = 'os-linux';
            else if (device.os && device.os.includes('Windows')) osClass = 'os-windows';
            else if (device.os && device.os.includes('Router')) osClass = 'os-router';
            else if (device.os && device.os.includes('IoT')) osClass = 'os-iot';
            
            row.innerHTML = `
                <td>${device.ip || 'Unknown'}</td>
                <td>${device.mac || 'Unknown'}</td>
                <td class="${osClass}">${device.os || 'Unknown'}</td>
                <td>${device.vendor || 'Unknown'}</td>
                <td>${device.ports ? device.ports.join(', ') : 'None'}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            `;
        });
    }
    
    function exportToCSV() {
        if (devices.length === 0) {
            alert('Nenhum dispositivo para exportar!');
            return;
        }
        
        let csv = 'IP Address,MAC Address,OS Type,Vendor,Open Ports,Status\n';
        
        devices.forEach(device => {
            const status = device.status === 'online' ? 'Online' : 'Offline';
            csv += `"${device.ip || ''}","${device.mac || ''}","${device.os || ''}","${device.vendor || ''}","${device.ports ? device.ports.join(',') : ''}","${status}"\n`;
        });
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.href = url;
        link.setAttribute('download', `network_scan_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    function toggleTheme() {
        const body = document.body;
        if (themeCheckbox.checked) {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
            themeLabel.textContent = 'Light Mode';
        } else {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            localStorage.setItem('theme', 'light');
            themeLabel.textContent = 'Dark Mode';
        }
    }
    
    function loadThemePreference() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        if (savedTheme === 'dark') {
            themeCheckbox.checked = true;
            document.body.classList.add('dark-theme');
            themeLabel.textContent = 'Light Mode';
        } else {
            themeCheckbox.checked = false;
            document.body.classList.add('light-theme');
            themeLabel.textContent = 'Dark Mode';
        }
    }
    
    function handleBeforeUnload(e) {
        if (isScanning) {
            e.preventDefault();
            e.returnValue = 'O escaneamento está em andamento. Tem certeza que deseja sair?';
            return e.returnValue;
        }
    }
});