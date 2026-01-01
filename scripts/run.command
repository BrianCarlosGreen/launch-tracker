#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Starting Orbital Launch Tracker (Docker only)..."
echo "This will build images and download the GCAT dataset on first run."

docker compose up --build
