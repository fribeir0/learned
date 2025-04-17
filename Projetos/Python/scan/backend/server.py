from flask import Flask, render_template, request
from flask_socketio import SocketIO
from scanner import NetworkScanner
import os
from threading import Lock
import eventlet
import logging

# Configuração do eventlet
eventlet.monkey_patch()

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config['SECRET_KEY'] = os.urandom(24).hex()

# Configuração robusta do SocketIO
socketio = SocketIO(app,
                   cors_allowed_origins="*",
                   async_mode='eventlet',
                   engineio_logger=True,
                   logger=True,
                   ping_timeout=60,
                   ping_interval=25)

scanner = NetworkScanner()
scan_lock = Lock()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('NetworkScannerServer')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    socketio.emit('connection_response', {
        'status': 'connected',
        'client_id': request.sid
    })

@socketio.on('start_scan')
def handle_start_scan(data):
    network = data.get('network', '192.168.0')
    scan_type = data.get('scan_type', 'common')
    
    with scan_lock:
        if not scanner._stop_flag and scanner.devices:
            socketio.emit('scan_update', {
                'type': 'error',
                'message': 'Scan already in progress'
            })
            return
            
    def progress_callback(data):
        socketio.emit('scan_update', {
            **data,
            'client_id': request.sid
        })
        
    socketio.start_background_task(
        target=scan_task,
        network=network,
        scan_type=scan_type,
        callback=progress_callback
    )

def scan_task(network, scan_type, callback):
    try:
        scanner.reset()
        callback({
            'type': 'status',
            'message': f'Starting {scan_type} scan on {network}'
        })
        
        success = scanner.scan_network(
            network=network,
            scan_type=scan_type,
            callback=callback
        )
        
        if success:
            callback({
                'type': 'complete',
                'data': scanner.get_results()
            })
        else:
            callback({
                'type': 'error',
                'message': 'Scan interrupted'
            })
            
    except Exception as e:
        logger.error(f"Scan error: {str(e)}")
        callback({
            'type': 'error',
            'message': f'Scan failed: {str(e)}'
        })

@socketio.on('stop_scan')
def handle_stop_scan():
    scanner.stop_scan()
    socketio.emit('scan_update', {
        'type': 'status',
        'message': 'Scan stopped by user',
        'client_id': request.sid
    })

if __name__ == '__main__':
    socketio.run(app,
                host='0.0.0.0',
                port=5000,
                debug=True,
                use_reloader=False,
                log_output=True)