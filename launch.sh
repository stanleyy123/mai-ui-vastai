#!/bin/bash
# Launch a mai-ui instance with correct settings.
# Usage: ./launch.sh [max_price_per_hr]
# Example: ./launch.sh 0.45

set -e

MAX_PRICE=${1:-0.45}
IMAGE="ghcr.io/stanleyy123/mai-ui-vastai:latest"
DISK=10
LABEL="mai_ui"

echo "==> Searching for RTX 4090 under \$${MAX_PRICE}/hr (on-demand, reliability > 0.95)..."
echo ""
vastai search offers \
  "gpu_name=RTX_4090 num_gpus=1 dph_total < ${MAX_PRICE} reliability > 0.95 rented=False" \
  --order 'dph_total' \
  --limit 10

echo ""
read -p "Enter offer ID to rent (ctrl-c to cancel): " OFFER_ID

vastai create instance "$OFFER_ID" \
  --image "$IMAGE" \
  --disk "$DISK" \
  --label "$LABEL" \
  --onstart-cmd "/app/start.sh"

echo ""
echo "==> Instance created. Monitor status:  vastai show instances"
echo "==> When done, destroy (not stop!):    vastai destroy instance <ID>"
