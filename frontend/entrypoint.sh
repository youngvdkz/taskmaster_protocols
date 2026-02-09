#!/usr/bin/env sh
set -e

PORT_VALUE="${PORT:-3000}"
if [ "$PORT_VALUE" = "undefined" ] || [ -z "$PORT_VALUE" ]; then
  PORT_VALUE=3000
fi

exec npx serve -s dist -l "$PORT_VALUE"
