import subprocess
import logging

def run_metabigor(domain: str):
    logger = logging.getLogger(__name__)
    try:
        result = subprocess.run(["metabigor", "intel", "-t", domain, "-o", "-"], capture_output=True, text=True, check=True)
        output = result.stdout.strip().split("\n")
        logger.info(f"Metabigor encontrou {len(output)} linhas para {domain}")
        return {"status": "ok", "output": output}
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro Metabigor: {e.stderr}")
        return {"status": "error", "error": e.stderr.strip(), "output": []}
