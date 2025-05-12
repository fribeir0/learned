import subprocess

def run_metabigor(domain: str):
    try:
        result = subprocess.run(
            ["metabigor", "intel", "-t", domain, "-o", "-"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip().split("\n")
        return {"status": "ok", "output": output}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr.strip(), "output": []}
