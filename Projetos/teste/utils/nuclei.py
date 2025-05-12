import subprocess

def run_nuclei(urls: list):
    input_data = "\n".join(urls)
    try:
        result = subprocess.run(
            ["nuclei", "-silent", "-json"],
            input=input_data,
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "ok", "output": result.stdout.strip().split("\n")}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr.strip(), "output": []}
