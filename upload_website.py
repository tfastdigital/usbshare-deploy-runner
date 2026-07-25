#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

HOST = os.environ["WEB_HOST"]
PORT = os.environ.get("WEB_PORT", "65002")
USER = os.environ["WEB_USER"]
PASS = os.environ["WEB_PASS"]
ROOT = f"/home/{USER}/domains/tfastdigital.com/public_html"

cfg = {
    "controlUrl": "http://31.97.99.137:5088",
    "downloadUrl": "https://tfastdigital.com/Gsm-usb-server",
    "currentVersion": "2.1.0",
    "minimumCustomerVersion": "2.1.0",
    "minimumTechnicianVersion": "2.1.0",
    "status": "ok",
    "message": "",
}
Path("/tmp/service-config.json").write_text(json.dumps(cfg, indent=2) + "\n")
Path("/tmp/service-config.php").write_text(
    """<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-store, max-age=0');
echo json_encode([
  'controlUrl' => 'http://31.97.99.137:5088',
  'downloadUrl' => 'https://tfastdigital.com/Gsm-usb-server',
  'currentVersion' => '2.1.0',
  'minimumCustomerVersion' => '2.1.0',
  'minimumTechnicianVersion' => '2.1.0',
  'status' => 'ok',
  'message' => '',
], JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
"""
)
Path("/tmp/htaccess").write_text(
    """<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^service-config$ service-config.php [L]
</IfModule>
DirectoryIndex service-config.php index.php
"""
)

env = os.environ.copy()
env["SSHPASS"] = PASS


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd[:8]), "...")
    r = subprocess.run(cmd, env=env)
    if r.returncode != 0:
        sys.exit(r.returncode)


ssh = [
    "sshpass",
    "-e",
    "ssh",
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "UserKnownHostsFile=/dev/null",
    "-o",
    "ConnectTimeout=40",
    "-p",
    PORT,
    f"{USER}@{HOST}",
]
scp = [
    "sshpass",
    "-e",
    "scp",
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "UserKnownHostsFile=/dev/null",
    "-o",
    "ConnectTimeout=40",
    "-P",
    PORT,
]
run(ssh + [f"mkdir -p {ROOT}/api/gsm-usb-server && ls -la {ROOT} | head"])
for local, remote in [
    ("/tmp/service-config.json", f"{ROOT}/gsm-usb-server-service.json"),
    ("/tmp/service-config.json", f"{ROOT}/api/gsm-usb-server/service-config.json"),
    ("/tmp/service-config.json", f"{ROOT}/api/gsm-usb-server/service-config"),
    ("/tmp/service-config.php", f"{ROOT}/api/gsm-usb-server/service-config.php"),
    ("/tmp/service-config.php", f"{ROOT}/api/gsm-usb-server/index.php"),
    ("/tmp/htaccess", f"{ROOT}/api/gsm-usb-server/.htaccess"),
]:
    run(scp + [local, f"{USER}@{HOST}:{remote}"])
run(ssh + [f"ls -la {ROOT}/api/gsm-usb-server; head -c 300 {ROOT}/gsm-usb-server-service.json; echo"])
print("website deploy done")
