#!/bin/bash
# Setup daily cron job for TikTok Drama Generator
# Run this script once to enable automatic daily video generation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$SCRIPT_DIR/daily_run.sh"

# Replace existing crontab if any
(crontab -l 2>/dev/null || true) | {
    read -r crontab
    if [ -n "$crontab" ]; then
        echo "$crontab"
    fi
    echo "0 6 * * * cd $SCRIPT_DIR && $RUNNER >> $SCRIPT_DIR/logs/cron.log 2>&1"
} | crontab -

echo "✅ Cron job installed: runs daily at 06:00"
echo "   Logs will be written to: $SCRIPT_DIR/logs/cron.log"
echo "   To view: crontab -l"
echo "   To remove: crontab -r"
