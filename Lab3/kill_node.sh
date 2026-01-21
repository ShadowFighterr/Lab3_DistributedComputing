#!/usr/bin/env bash
# Usage: ./kill_node.sh <node_id>
NODE_ID=$1
if [ -z "$NODE_ID" ]; then
echo "Usage: $0 <node_id>"
exit 1
fi
# find python process running node.py with --id <NODE_ID>
PIDS=$(ps aux | grep node.py | grep "--id $NODE_ID" | grep -v grep | awk '{print $2}')
if [ -z "$PIDS" ]; then
echo "No process found for node $NODE_ID"
exit 1
fi
for p in $PIDS; do
kill -9 $p
echo "Killed $p"
done