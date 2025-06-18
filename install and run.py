import os
import subprocess
import sys

REPO_URL = "https://github.com/Glory237107/smart_port_scanner.git"
INSTALL_DIR = os.path.expanduser("~/smart_port_scanner")
VENV_DIR = os.path.join(INSTALL_DIR, "venv")
MAIN_SCRIPT = "main.py"

def run_command(command, cwd=None):
    print(f" Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f" Error: {result.stderr}")
    else:
        print(result.stdout)

def setup():
    print(" Setting up your smart port scanner...")

    # Clone or pull repo
    if os.path.exists(INSTALL_DIR):
        print(" Repo already exists, pulling latest changes...")
        run_command(["git", "pull", "origin", "main"], cwd=INSTALL_DIR)
    else:
        print(" Cloning the repo...")
        run_command(["git", "clone", REPO_URL, INSTALL_DIR])

    # Create virtualenv
    print(" Creating virtual environment...")
    run_command(["python3", "-m", "venv", "venv"], cwd=INSTALL_DIR)

    # Activate venv and install dependencies
    print(" Installing dependencies...")
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    req_path = os.path.join(INSTALL_DIR, "requirements.txt")
    if os.path.exists(req_path):
        run_command([pip_path, "install", "--upgrade", "pip"])
        run_command([pip_path, "install", "-r", req_path])
    else:
        print(" No requirements.txt file found!")

    # Run the script in background
    print(" Launching scanner in the background...")
    python_path = os.path.join(VENV_DIR, "bin", "python")
    log_file = os.path.join(INSTALL_DIR, "scanner.log")
    subprocess.Popen(
        [python_path, os.path.join(INSTALL_DIR, MAIN_SCRIPT)],
        stdout=open(log_file, 'a'),
        stderr=subprocess.STDOUT
    )
    print(f" All done! Check {log_file} for logs.")

if __name__ == "__main__":
    setup()

