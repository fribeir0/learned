import subprocess

def run_naabu(targets: list):
    input_data = "\n".join(targets)
    try:
        result = subprocess.run(
            ["naabu", "-silent"],
            input=input_data,
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "ok", "output": result.stdout.strip().split("\n")}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr.strip(), "output": []}
