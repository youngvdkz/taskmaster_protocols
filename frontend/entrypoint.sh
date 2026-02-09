#!/usr/bin/env sh
set -e

PORT_VALUE="${PORT:-3000}"
if [ "$PORT_VALUE" = "undefined" ] || [ -z "$PORT_VALUE" ]; then
  PORT_VALUE=3000
fi
case "$PORT_VALUE" in
  ''|*[!0-9]*)
    PORT_VALUE=3000
    ;;
esac

exec npx serve -s dist -l "0.0.0.0:${PORT_VALUE}"
