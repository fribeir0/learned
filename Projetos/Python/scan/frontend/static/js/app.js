document.addEventListener('DOMContentLoaded', function() {
    // Elementos da interface
    const scanBtn = document.getElementById('scanButton');
    const loadingIndicator = document.getElementById('loading');
    const statusDisplay = document.getElementById('status-message');
    const devicesTable = document.getElementById('devicesTable').getElementsByTagName('tbody')[0];
    
    // Conecta ao servidor Socket.IO
    const socket = io();
    
    // Atualiza os contadores do resumo
    function updateSummary(data) {
        document.getElementById('total-devices').textContent = data.total_devices;
        document.getElementById('linux-count').textContent = data.linux_count;
        document.getElementById('windows-count').textContent = data.windows_count;
        document.getElementById('unknown-count').textContent = data.unknown_count;
    }
    
    // Adiciona um dispositivo à tabela
    function addDevice(device) {
        const row = devicesTable.insertRow();
        row.className = `device-row ${device.status}`;
        
        row.innerHTML = `
            <td>${device.ip}</td>
            <td>${device.mac}</td>
            <td class="os ${device.os.toLowerCase()}">${device.os}</td>
            <td>${device.ports?.join(', ') || '-'}</td>
            <td class="status">${device.status === 'online' ? 'Online' : 'Sem ICMP'}</td>
        `;
    }
    
    // Limpa a tabela de dispositivos
    function clearDevices() {
        devicesTable.innerHTML = '';
    }
    
    // Eventos Socket.IO
    socket.on('connect', () => {
        console.log('Conectado ao servidor');
        statusDisplay.textContent = 'Pronto para escanear';
        scanBtn.disabled = false;
    });
    
    socket.on('disconnect', () => {
        statusDisplay.textContent = 'Desconectado do servidor';
    });
    
    socket.on('scan_update', (data) => {
        console.log('Atualização recebida:', data);
        
        switch(data.type) {
            case 'status':
                statusDisplay.textContent = data.message;
                break;
                
            case 'device':
                addDevice(data.data.device);
                updateSummary(data.data.summary);
                break;
                
            case 'complete':
                statusDisplay.textContent = 'Scan completo!';
                scanBtn.disabled = false;
                loadingIndicator.classList.add('hidden');
                updateSummary(data.data.summary);
                break;
                
            case 'error':
                statusDisplay.textContent = data.message;
                scanBtn.disabled = false;
                loadingIndicator.classList.add('hidden');
                alert(`Erro: ${data.message}`);
                break;
        }
    });
    
    // Evento do botão de scan
    scanBtn.addEventListener('click', () => {
        scanBtn.disabled = true;
        loadingIndicator.classList.remove('hidden');
        statusDisplay.textContent = 'Iniciando scan...';
        clearDevices();
        socket.emit('start_scan');
    });
});