#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "======================================================"
echo "🚀 Starting ClinicPilot AI MVP"
echo "======================================================"

# 1. Check for required API Keys
if [ -z "$DEEPSEEK_API_KEY" ] && [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: API Key is missing."
    echo "Please export DEEPSEEK_API_KEY or OPENROUTER_API_KEY before running this script."
    echo "Example: export DEEPSEEK_API_KEY=\"your-api-key-here\""
    exit 1
fi
echo "✅ API Key verified."

# 2. (Optional) Activate Conda environment if it exists
# If the user is running this in the base environment or a venv, this won't break it.
if command -v conda &> /dev/null; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if conda env list | grep -q "dkl"; then
        echo "✅ Activating Conda environment: dkl"
        conda activate dkl
    fi
fi

# 3. Start the FastAPI application
echo "⏳ Starting FastAPI server..."
echo "⚠️  Please wait for 'Application startup complete.' before opening the browser."
echo "------------------------------------------------------"

uvicorn backend.main:app --host 0.0.0.0 --port 8088 --reload