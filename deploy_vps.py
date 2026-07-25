#!/usr/bin/env python3
import os
import subprocess
import sys

HOST = os.environ["VPS_HOST"]
USER = os.environ["VPS_USER"]
PASS = os.environ["VPS_PASSWORD"]
PKG = os.environ.get("PKG_URL", "https://litter.catbox.moe/8z1bts.tgz")

env = os.environ.copy()
env["SSHPASS"] = PASS
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
    f"{USER}@{HOST}",
]
script = f"""set -e
systemctl stop usbshare-api || true
docker rm -f usbshare-api || true
fuser -k 5088/tcp || true
fuser -k 5089/tcp || true
fuser -k 5090/tcp || true
mkdir -p /opt/usbshare/api
curl -fL --retry 8 -o /tmp/api.tgz {PKG}
rm -rf /opt/usbshare/api/*
tar -xzf /tmp/api.tgz -C /opt/usbshare/api
chmod +x /opt/usbshare/api/UsbShare.Cloud.Api
if [ -f /opt/usbshare/api/install-usbshare-api.sh ]; then
  bash /opt/usbshare/api/install-usbshare-api.sh
else
  cat >/etc/systemd/system/usbshare-api.service <<'UNIT'
[Unit]
Description=GSM USB Server Cloud API
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
WorkingDirectory=/opt/usbshare/api
ExecStart=/opt/usbshare/api/UsbShare.Cloud.Api
Restart=always
RestartSec=3
Environment=ASPNETCORE_ENVIRONMENT=Production
Environment=ASPNETCORE_URLS=http://0.0.0.0:5088
Environment=DataPlane__PublicHost=31.97.99.137
Environment=DataPlane__Port=5089
Environment=DataPlane__UsbIpPort=5090
Environment=LocalDiscovery__Enabled=false
Environment=NetworkSecurity__AllowPrivateNetworks=true
Environment=NetworkSecurity__BlockVpnOrProxy=false
Environment=NetworkSecurity__BlockHostingOrDatacenter=false
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
UNIT
  systemctl daemon-reload
  systemctl enable usbshare-api
  systemctl restart usbshare-api
fi
sleep 3
curl -fsS http://127.0.0.1:5088/health; echo
curl -fsS http://127.0.0.1:5088/api/service; echo
"""
r = subprocess.run(ssh + [script], env=env)
sys.exit(r.returncode)
