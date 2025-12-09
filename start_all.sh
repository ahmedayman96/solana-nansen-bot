#!/bin/bash
# Run both Bot and Dashboard in parallel
# Press Ctrl+C to stop both

echo "Starting Solana Nansen Bot & Dashboard..."

(trap 'kill 0' SIGINT; \
 python3 main.py & \
 cd dashboard && npm run dev)
