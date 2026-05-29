#!/usr/bin/env bash
# Run TabQA Generator locally using the gradino virtualenv.
# Prerequisites: gradino/env/ must exist (see gradino/README for setup).
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GRADINO_ENV="$SCRIPT_DIR/gradino/env"
PYTHON="$GRADINO_ENV/bin/python3"
PIP="$GRADINO_ENV/bin/pip"

if [ ! -f "$PYTHON" ]; then
    echo "ERROR: $PYTHON not found."
    echo "Set up the gradino environment first, e.g.:"
    echo "  cd gradino && python3.13 -m venv env && env/bin/pip install -r requirements.txt"
    exit 1
fi

echo "Python: $PYTHON  ($(\"$PYTHON\" --version))"

# Install backend deps into the gradino env (idempotent)
echo "Ensuring backend dependencies are installed..."
"$PIP" install --quiet fastapi "uvicorn[standard]" python-multipart aiofiles

# Load OPENAI_API_KEY from gradino/.env if not already in environment
if [ -z "$OPENAI_API_KEY" ] && [ -f "$SCRIPT_DIR/gradino/.env" ]; then
    KEY=$(grep -v '^#' "$SCRIPT_DIR/gradino/.env" | grep 'OPENAI_API_KEY' | head -1 | cut -d'=' -f2- | tr -d '"'"'" | xargs)
    if [ -n "$KEY" ]; then
        export OPENAI_API_KEY="$KEY"
        echo "Loaded OPENAI_API_KEY from gradino/.env"
    fi
fi

export GRADINO_PATH="$SCRIPT_DIR/gradino"

echo ""
echo "Starting TabQA Generator → http://localhost:8000"
echo ""
cd "$SCRIPT_DIR/backend"
exec "$PYTHON" -m uvicorn app:app --host 0.0.0.0 --port 8000 --log-level info
