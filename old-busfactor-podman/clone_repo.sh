#!/bin/sh
set -e

if [ -z "$REPO_URL" ]; then
    echo "[!] Error: REPO_URL is not set." >&2
    exit 1
fi

echo "[*] Cleaning up previous workspace directories..."
rm -rf /workspace/repo /workspace/repo.tmp

echo "[*] Cloning $REPO_URL into /workspace/repo.tmp..."
git clone "$REPO_URL" /workspace/repo.tmp

echo "[*] Moving completed clone to /workspace/repo..."
mv /workspace/repo.tmp /workspace/repo

echo "[+] Repository cloned successfully."

