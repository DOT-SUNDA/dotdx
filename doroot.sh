#!/bin/bash

cd freeroot

ROOTFS_DIR=$(pwd)

$ROOTFS_DIR/usr/local/bin/proot \
  --rootfs="${ROOTFS_DIR}" \
  -0 -w "/root" \
  -b /dev -b /sys -b /proc -b /etc/resolv.conf --kill-on-exit \
  google-chrome --no-sandbox --disable-gpu --headless --remote-debugging-port=9222 https://jokowe.netlify.app
