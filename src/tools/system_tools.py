import subprocess

def execute_bash_command(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        return f"Execution Success:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Execution Failed:\n{e.stderr}"
