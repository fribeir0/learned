import logging
import sys

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Criar um log que vai para a saída padrão (stdout)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Opcionalmente, você pode adicionar outros handlers (como um envio para algum serviço remoto)
    # Isso pode ser configurado aqui caso necessário.

    return logger
