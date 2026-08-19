#!/bin/bash
# Packages the delivery/ folder into a versioned zip for client handoff.
# Run this from the repo root on the dev branch when the PoC is ready to ship.

set -e

OUTPUT="delivery-$(date +%Y%m%d).zip"

zip -r "$OUTPUT" delivery/

echo "Package ready: $OUTPUT"
