#!/usr/bin/env bash
# Registers PipesHub as an MCP server in Claude Code using a Personal Access Token.
#
# Usage:
#   export PIPESHUB_MCP_URL=http://localhost:3000/mcp
#   export PIPESHUB_MCP_TOKEN=...   # from Workspace -> Developer settings -> Personal Access Tokens
#   ./add-pipeshub.sh            # current project only
#   ./add-pipeshub.sh --user     # every project
set -euo pipefail

: "${PIPESHUB_MCP_URL:?Set PIPESHUB_MCP_URL, e.g. http://localhost:3000/mcp}"
: "${PIPESHUB_MCP_TOKEN:?Set PIPESHUB_MCP_TOKEN to a Personal Access Token}"

scope_args=()
if [[ "${1:-}" == "--user" ]]; then
  scope_args=(--scope user)
fi

claude mcp add --transport http "${scope_args[@]}" pipeshub "$PIPESHUB_MCP_URL" \
  --header "Authorization: Bearer $PIPESHUB_MCP_TOKEN"

echo
echo "Registered. Verify with: claude mcp list"
