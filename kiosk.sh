#!/bin/bash

# Clean up any WAV files that are left in the queue.
# rm /home/pi/Code/birdnetlib-listener-device/audio/inbox/*.wav
find /home/pi/Code/birdnetlib-listener-device/audio/inbox -type f -name '*.wav' -delete

# Delay so the docker container has time to start.
url="http://localhost:8000/static/dist/index.html"  # Replace with the URL you want to check
status_code=0

# Loop until a 200 OK response is received
until [ "$status_code" -eq 200 ]; do
    echo "Checking URL..."
    # Use curl to get the HTTP status code
    status_code=$(curl -o /dev/null -s -w "%{http_code}\n" "$url")

    if [ "$status_code" -eq 200 ]; then
        echo "Received 200 OK, continuing..."
    else
        echo "Service unavailable, retrying..."
        sleep 2  # Wait for 10 seconds before retrying
    fi
done


# Check if Firefox ESR is installed
if ! command -v firefox-esr >/dev/null 2>&1; then
    echo "Firefox ESR is not installed. Installing now..."
    sudo apt-get update
    sudo apt-get install -y firefox-esr
else
    echo "Firefox ESR is already installed."
fi

# Update from github
cd /home/pi/Code/birdnetlib-listener-device; git pull
cd /home/pi/Code/birdnetlib-listener-device; docker compose -f docker-compose.rpi.yml exec web python manage.py migrate

sleep 5

xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

# For Chromium ... not using by default.
# sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
# sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences
# /usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk "http://localhost:8000/static/dist/index.html" --disk-cache-dir=/dev/null --disk-cache-size=1 &

sudo -u pi firefox --display=:0 --kiosk-monitor 0 "http://localhost:8000/static/dist/index.html" -kiosk &

while true; do
   # xdotool keydown ctrl+Tab; xdotool keyup crtl+Tab;
   sleep 5
done
