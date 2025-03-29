document.addEventListener('DOMContentLoaded', function() {
    const scanButton = document.getElementById('scanButton');
    const loadingElement = document.getElementById('loading');
    
    scanButton.addEventListener('click', startScan);
    
    function startScan() {
        scanButton.disabled = true;
        loadingElement.classList.remove('hidden');
        
        fetch('/api/scan', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                checkScanProgress();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            scanButton.disabled = false;
            loadingElement.classList.add('hidden');
        });
    }
    
    function checkScanProgress() {
        fetch('/api/results')
        .then(response => response.json())
        .then(data => {
            if(data.summary.scan_time) {
                updateUI(data);
                scanButton.disabled = false;
                loadingElement.classList.add('hidden');
            } else {
                setTimeout(checkScanProgress, 2000);
            }
        });
    }
    
    function updateUI(data) {
        // Atualiza sumário
        const summarySection = document.querySelector('.summary-section');
        summarySection.classList.remove('hidden');
        
        const summaryCards = document.querySelector('.summary-cards');
        summaryCards.innerHTML = `
            <div class="summary-card">
                <h3>Dispositivos</h3>
                <div class="count">${data.summary.total_devices}</div>
            </div>
            <div class="summary-card">
                <h3>Linux</h3>
                <div class="count">${data.summary.linux_count}</div>
            </div>
            <div class="summary-card">
                <h3>Windows</h3>
                <div class="count">${data.summary.windows_count}</div>
            </div>
        `;
        
        // Atualiza tabela
        const devicesSection = document.querySelector('.devices-section');
        devicesSection.classList.remove('hidden');
        
        const tbody = document.querySelector('#devicesTable tbody');
        tbody.innerHTML = data.devices.map(device => `
            <tr>
                <td>${device.ip}</td>
                <td>${device.mac}</td>
                <td class="os-${device.os.toLowerCase()}">${device.os}</td>
                <td>${device.ports.join(', ') || 'Nenhuma'}</td>
            </tr>
        `).join('');
    }
});