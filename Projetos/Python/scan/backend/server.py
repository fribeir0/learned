from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from scanner import NetworkScanner
import threading
import os
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__,
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/templates'))),
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/static'))

app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")

scanner = NetworkScanner()
scan_active = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.info('Cliente conectado: %s', request.sid)
    emit('connection_response', {'status': 'connected'})

@socketio.on('start_scan')
def handle_start_scan():
    global scan_active
    
    if scan_active:
        emit('scan_update', {'type': 'error', 'message': 'Scan já está em andamento'})
        return
    
    scan_active = True
    
    def scan_task():
        try:
            logger.info("Iniciando scan de rede")
            emit('scan_update', {'type': 'status', 'message': 'Iniciando scan...'})
            
            def progress_callback(device_data):
                emit('scan_update', {
                    'type': 'device',
                    'data': device_data
                })
                socketio.sleep(0)  # Permite que o Socket.IO envie a mensagem
            
            scanner.set_update_callback(progress_callback)
            
            # Executa o scan
            network = "192.168.0"  # Altere conforme sua rede
            scanner.scan_network(network, scan_ports=True)
            
            emit('scan_update', {
                'type': 'complete',
                'data': scanner.get_results()
            })
            
        except Exception as e:
            logger.error("Erro durante o scan: %s", str(e))
            emit('scan_update', {
                'type': 'error',
                'message': f"Erro durante o scan: {str(e)}"
            })
        finally:
            global scan_active
            scan_active = False
    
    # Inicia a thread de scan
    socketio.start_background_task(scan_task)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, use_reloader=False)