#!/bin/bash

echo "-=-=- Airlines Manager Bot -=-=-"
echo "Ready to execute commands!"
echo "Start the tasks manually by running:"
echo "    docker exec -it airlines-manager-bot python3 main.py"

echo ""
echo "Entering main loop execution!"
while true; do
  python3 main.py
  echo "Sleeping for 8 hours before running again..."
  sleep 28800
done
