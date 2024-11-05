import os
import shutil
import subprocess
import sys
import time
import requests
import threading
import base64

PUB_KEY = base64.b64decode(os.getenv("PUB_KEY_ENCODED")).decode('utf-8')
PRVT_KEY = base64.b64decode(os.getenv("PRVT_KEY_ENCODED")).decode('utf-8')
HOST_PRVT_KEY = base64.b64decode(os.getenv("HOST_PRVT_KEY_ENCODED")).decode('utf-8')
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def change_password(username="runneradmin", new_password="@entoto-mar21YAM"):
    subprocess.run(["net", "user", username, new_password], check=True)

def extract_files():
    shutil.unpack_archive('rclone.zip')
    shutil.unpack_archive('stunserver_win64_1_2_16.zip')
    shutil.unpack_archive('OpenSSH-Win64.zip')
    subprocess.run(["7z", "e", "nmap-7.80-setup.zip"], check=True)
    subprocess.run(["7z", "e", "cloudflared.7z"], check=True)

def install_packages():
    subprocess.run(["msiexec", "/i", "winfsp.msi", "/qn"], check=True)
    subprocess.run(["msiexec", "/i", "wireguard-amd64-0.5.3.msi", "/qn"], check=True)
    subprocess.run([".\\nmap-7.80-setup.exe", "/S"], check=True)

def setup_ssh_server():
    os.makedirs("OpenSSH-Win64\\ssh", exist_ok=True)
    os.makedirs(os.path.expanduser("~\\.ssh"), exist_ok=True)
    
    ssh_config = """
HostKey ssh/ssh_host_rsa_key
Subsystem sftp sftp-server.exe
LogLevel DEBUG3
PidFile ssh/sshd.pid
"""
    with open("OpenSSH-Win64\\ssh\\sshd_config", "w") as f:
        f.write(ssh_config)
    
    # Write the SSH keys
    with open(os.path.expanduser("~\\.ssh\\authorized_keys"), "w") as f:
        f.write(PUB_KEY)
    with open(os.path.expanduser("~\\.ssh\\id_rsa"), "w") as f:
        f.write(PRVT_KEY)
    with open("OpenSSH-Win64\\ssh\\ssh_host_rsa_key", "w") as f:
        f.write(HOST_PRVT_KEY)

    # Set permissions on SSH keys
    key_path = os.path.join(os.getcwd(), "OpenSSH-Win64\\ssh\\ssh_host_rsa_key")
    subprocess.run(["icacls", key_path, "/c", "/t", "/Inheritance:d"])
    subprocess.run(["icacls", key_path, "/c", "/t", "/Grant", f"{os.environ['USERNAME']}:F"])
    subprocess.run(["takeown", "/F", key_path])
    subprocess.run(["icacls", key_path, "/c", "/t", "/Grant:r", f"{os.environ['USERNAME']}:F"])
    subprocess.run(["icacls", key_path, "/c", "/t", "/Remove:g", "SYSTEM", "Users", "Administrators"])
    
    # Add firewall rule for SSH
    subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=Allow SSH", 
                    "dir=in", "action=allow", "protocol=TCP", "localport=22"])


def start_ssh_server():
    # Build absolute paths for sshd.exe and its config file
    sshd_path = os.path.abspath("OpenSSH-Win64\\sshd.exe")
    config_path = os.path.abspath("OpenSSH-Win64\\ssh\\sshd_config")

    # Start SSH server in the foreground for log visibility
    process = subprocess.Popen(
        [sshd_path, "-f", config_path, "-e"],
        text=True
    )

def clean_up():
    files_to_delete = [
        'stunserver_win64_1_2_16.zip', 'rclone.zip', 'OpenSSH-Win64.zip',
        'wireguard-amd64-0.5.3.msi', 'winfsp.msi', 'cloudflared.7z',
        'nmap-7.80-setup.exe', 'nmap-7.80-setup.zip', 'nmap-7.80-setup.z05',
        'nmap-7.80-setup.z04', 'nmap-7.80-setup.z03', 'nmap-7.80-setup.z02',
        'nmap-7.80-setup.z01'
    ]
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)

def start_cloudflared():
    # Start cloudflared and capture output
    process = subprocess.Popen(
        ["cloudflared.exe", "tunnel", "--no-autoupdate", "--url", "tcp://localhost:22"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Read stderr until the cloudflared link is found
    link = ''
    for line in process.stderr:
        if ".trycloudflare.com" in line:
            link = line.split()[3]
            break
    
    # Send the link to Telegram
    if link:
        telegram_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        params = {
            'chat_id': CHAT_ID,
            'text': link
        }
        requests.get(telegram_url, params=params)
    
    time.sleep(10000)  # Keep the process alive for 10,000 seconds to maintain the connection

if __name__ == "__main__":
    change_password()
    extract_files()
    install_packages()
    setup_ssh_server()
    start_ssh_server()  # Start SSH server in foreground to show logs in GitHub Actions
    clean_up()
    start_cloudflared()
