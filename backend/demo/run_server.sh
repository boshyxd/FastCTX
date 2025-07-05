#!/bin/bash
cd "$(dirname "$0")"
pip install -r requirements.txt
export OPENROUTER_API_KEY=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
python mcp_server.py