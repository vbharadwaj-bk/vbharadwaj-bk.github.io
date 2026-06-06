#!/usr/bin/env bash
#
# Build the site and report broken links with LinkChecker.
#
# Serves the built `output/` over HTTP (the dev build uses root-absolute URLs
# like /images/..., which don't resolve under file://) and crawls it.
#
# Environment variables:
#   LINKCHECK_PORT=8911   port for the temporary HTTP server
#   LINKCHECK_EXTERN=1    also verify external URLs (slower, needs network)
#   LINKCHECK_STRICT=1    exit non-zero when broken links are found
#                         (blocks the commit; otherwise the report is
#                         informational and the commit proceeds)
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT="${LINKCHECK_PORT:-8911}"
OUTPUT_DIR="$ROOT/output"
REPORT="$ROOT/linkcheck-report.txt"

echo "[linkcheck] Building site..."
if ! make html >/dev/null; then
  echo "[linkcheck] Build failed; skipping link check." >&2
  exit 1
fi

echo "[linkcheck] Serving output/ on port $PORT..."
python3 -m http.server "$PORT" --directory "$OUTPUT_DIR" >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null' EXIT

# Wait for the server to accept connections.
for _ in $(seq 1 20); do
  curl -sf "http://localhost:$PORT/" >/dev/null 2>&1 && break
  sleep 0.3
done

# By default only check internal links: fast and free of network flakiness.
# Set LINKCHECK_EXTERN=1 to also check external URLs.
if [ "${LINKCHECK_EXTERN:-0}" = "1" ]; then
  SCOPE_ARGS=(--check-extern)
  echo "[linkcheck] Checking internal and external links..."
else
  # Ignore any http(s) URL whose host is not localhost.
  SCOPE_ARGS=(--ignore-url '^https?://(?!localhost)')
  echo "[linkcheck] Checking internal links (set LINKCHECK_EXTERN=1 for external)..."
fi

linkchecker --no-warnings -o text "${SCOPE_ARGS[@]}" "http://localhost:$PORT/" \
  | tee "$REPORT"
STATUS=${PIPESTATUS[0]}

echo
if [ "$STATUS" -ne 0 ]; then
  echo "[linkcheck] Broken links found. Full report: $REPORT"
  [ "${LINKCHECK_STRICT:-0}" = "1" ] && exit 1
else
  echo "[linkcheck] No broken links found."
fi

# Informational by default — don't block the commit unless LINKCHECK_STRICT=1.
exit 0
