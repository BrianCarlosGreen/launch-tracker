#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Stopping Orbital Launch Tracker and deleting all data..."

docker compose down -v
