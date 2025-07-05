#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u
# The return value of a pipeline is the status of the last command to exit with a non-zero status, or zero if all commands exit successfully.
set -o pipefail

# --- Configuration ---
FASTCTX_PORT=8000
NEO4J_BOLT_PORT=7687
NEO4J_HTTP_PORT=7474

# --- Functions ---

handle_error() {
    local exit_code=$?
    local cmd="$BASH_COMMAND"
    echo "
❌ An error occurred (exit code: $exit_code) while executing: $cmd"
    echo "Please check the error message above for details."
    exit $exit_code
}

trap handle_error ERR

check_command() {
    if ! command -v "$1" &> /dev/null;
    then
        echo "
❌ Error: $1 is not installed or not in your PATH."
        echo "Please install $1 to proceed. Refer to its official documentation for installation instructions."
        exit 1
    fi
}

check_docker_compose() {
    if command -v docker-compose &> /dev/null;
    then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif command -v docker &> /dev/null && docker compose version &> /dev/null;
    then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        echo "
❌ Error: Docker Compose (v1 or v2) is not installed or not in your PATH."
        echo "Please install Docker Compose to proceed. Refer to https://docs.docker.com/compose/install/ for instructions."
        exit 1
    fi
    echo "Using Docker Compose command: $DOCKER_COMPOSE_CMD"
}

# --- Main Deployment Script ---

echo "🚀 Starting FastCTX Deployment..."

# 1. Check for necessary commands
echo "
Checking for required tools..."
check_command "docker"
check_docker_compose
echo "All required tools found. Proceeding with deployment."

# 2. Check for OPENAI_API_KEY (for OpenRouter)
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "
⚠️ Warning: OPENAI_API_KEY environment variable (which should contain your OpenRouter API key) is not set."
    echo "Indexing and context retrieval features will not work without it."
    echo "Please set it in your shell or create a .env file in the project root (e.g., OPENAI_API_KEY=sk-yourkey)."
    read -p "Do you want to continue without OPENAI_API_KEY? (y/N): " confirm_key
    if [[ ! "$confirm_key" =~ ^[yY]$ ]]; then
        echo "Aborting deployment. Please set OPENAI_API_KEY and try again."
        exit 1
    fi
else
    echo "OPENAI_API_KEY is set. Proceeding."
fi

# 3. Build Docker images
echo "
🏗️ Building Docker images..."
$DOCKER_COMPOSE_CMD build
echo "Docker images built successfully."

# 4. Start Docker containers
echo "
▶️ Starting Docker containers (FastCTX and Neo4j)..."
$DOCKER_COMPOSE_CMD up -d
echo "Docker containers started successfully."

# 5. Provide access information
echo "
✅ FastCTX deployment complete!"
echo "Your FastCTX server should now be running and accessible at: http://localhost:$FASTCTX_PORT"
echo "Neo4j Browser: http://localhost:$NEO4J_HTTP_PORT (User: neo4j, Password: password)"
echo "Neo4j Bolt: bolt://localhost:$NEO4J_BOLT_PORT"

# 6. Provide VS Code Copilot settings
echo "
--- VS Code Copilot MCP Server Settings ---"
echo "Add the following JSON configuration to your VS Code settings.json file:"
echo "(You can open it by pressing F1 and typing 'Preferences: Open User Settings (JSON)')
"

cat << EOF
{
    // ... other settings ...
    "mcp": {
        "servers": {
            "fastctx": {
                "type": "http",
                "url": "http://localhost:$FASTCTX_PORT/api/mcp",
                "name": "FastCTX MCP Server",
                "description": "Connects to your local FastCTX MCP server for code analysis and RAG."
            }
        }
    }
    // ... other settings ...
}
EOF

echo "
Remember to replace '... other settings ...' with your existing VS Code settings."
echo "If you don't have an 'mcp' section, you can add it directly."
echo "If you have an existing 'mcp' section, merge the 'servers' object."

echo "
To stop the containers, run: $DOCKER_COMPOSE_CMD down"