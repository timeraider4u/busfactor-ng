#!/bin/sh
set -e

if [ -z "$REPO_URL" ]; then
    echo "[!] Error: REPO_URL is not set." >&2
    exit 1
fi

echo "[*] Cleaning up previous workspace directories..."
rm -rf /workspace/repo /workspace/repo.tmp

DEPTH_ARG=""
if [ -n "$CLONE_DEPTH" ] && [ "$CLONE_DEPTH" -gt 0 ] 2>/dev/null; then
    DEPTH_ARG="--depth $CLONE_DEPTH"
    echo "[*] Using shallow clone depth: $CLONE_DEPTH"
fi

if [ -n "$BRANCH_NAME" ]; then
    SHORT_BRANCH="${BRANCH_NAME#origin/}"
    echo "[*] Cloning branch '$SHORT_BRANCH' of $REPO_URL..."
    git clone --single-branch --branch "$SHORT_BRANCH" $DEPTH_ARG "$REPO_URL" /workspace/repo.tmp
else
    echo "[*] Cloning all branches of $REPO_URL..."
    git clone $DEPTH_ARG "$REPO_URL" /workspace/repo.tmp
fi

echo "[*] Moving completed clone to /workspace/repo..."
mv /workspace/repo.tmp /workspace/repo

echo "[+] Repository cloned successfully."
