import subprocess

def run_subfinder(domain: str):
    try:
        result = subprocess.run(
            ["subfinder", "-d", domain, "-silent"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "ok", "output": result.stdout.strip().split("\n")}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr.strip(), "output": []}
