from flask import Flask, render_template, request
from flask_socketio import SocketIO
from scanner import NetworkScanner
import logging
import os
from threading import Lock

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config['SECRET_KEY'] = os.urandom(24).hex()

socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='threading',
                   logger=True,
                   engineio_logger=True)

scanner = NetworkScanner()
scan_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    logging.info(f"Client connected: {client_id}")
    socketio.emit('connection_response', 
                 {'status': 'connected', 'client_id': client_id},
                 room=client_id)

@socketio.on('start_scan')
def handle_start_scan(data):
    network = data.get('network', '192.168.0')
    
    with scan_lock:
        if scanner._stop_flag is False and len(scanner.devices) > 0:
            socketio.emit('scan_update', {
                'type': 'error',
                'message': 'Scan already in progress'
            })
            return
    
    def progress_callback(data):
        socketio.emit('scan_update', {
            'type': 'progress',
            'data': data
        })
    
    socketio.start_background_task(target=scan_task, network=network, callback=progress_callback)

def scan_task(network, callback):
    try:
        scanner.reset()
        socketio.emit('scan_update', {
            'type': 'status',
            'message': 'Starting network scan...'
        })
        
        success = scanner.scan_network(network, callback)
        
        if success:
            results = scanner.get_results()
            socketio.emit('scan_update', {
                'type': 'complete',
                'data': results
            })
        else:
            socketio.emit('scan_update', {
                'type': 'error',
                'message': 'Scan was interrupted'
            })
    except Exception as e:
        logging.error(f"Scan error: {str(e)}")
        socketio.emit('scan_update', {
            'type': 'error',
            'message': f"Scan error: {str(e)}"
        })

@socketio.on('stop_scan')
def handle_stop_scan():
    scanner.stop_scan()
    socketio.emit('scan_update', {
        'type': 'status',
        'message': 'Scan stopped by user'
    })

if __name__ == '__main__':
    socketio.run(app, 
                host='0.0.0.0', 
                port=5000, 
                debug=True,
                use_reloader=False,
                allow_unsafe_werkzeug=True)