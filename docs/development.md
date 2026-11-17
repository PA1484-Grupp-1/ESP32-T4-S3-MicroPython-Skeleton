# Development

This guide explains how to develop/configure the ESP32 project. It focuses on Trafiklab API used to show public transport departures.

# Setup

1. Open the project in VS
2. Run project/create_secrets.bat to create secrets_env.py
3. Add your wifi credentials and trafiklab API key. 
4. Connect the ESP32 board.  


# Trafiklab API

The project uses the Trafiklab Realtime API to get public transport departures.

("https://realtime-api.trafiklab.se/v1/departures/"
                          "{STOP_GROUP_ID}?key={API_KEY}")

Replace {STOP_GROUP_ID} and {API_KEY} with your values.

The API returns depature times, delays, destination, and transport types. Stop IDs are listed in project/stations.py

# API Documentation
- Trafiklab Realtime API: 
https://www.trafiklab.se/api/our-apis/trafiklab-realtime-apis/

# Quality Assurance

We use code review and manual testing on the device.

## Code review
- All changes are made on a branch and merged through a pull request.
- At least one other group member reviews the pull request before it is merged.
- The reviewer checks that the code follows the coding standard (PEP 8), has comments and does not change the skeleton files (`support/`, `boards/`, `platformio/`, `firmware/`).

## Manual testing
Run this checklist on the device before merging changes that affect the app.

| Test | Expected result |
| --- | --- |
| Start the device (US1.1) | Start screen shows project name, version, group and members |
| Swipe down/right/left (US2.1, US3.1) | Moves between start, departures and settings screens |
| Open departures (US1.2B) | Line, destination, time and status are shown for the selected stop |
| Select another stop (US3.2B) | Departure table changes to the new stop |
| Select Bus/Train/Ferry/All (US3.3) | Only the selected transport type is shown |
| Save Default, restart the device (US3.4) | Saved stop and transport type are restored |
| Change settings, press Reset to Default (US3.5) | Settings go back to the saved default |
| Wait 60 seconds (US4.1) | Departure table updates by itself |
| Press the refresh button (US4.2) | Departure table updates |
| Open settings (US4.3) | Wi-Fi and live data status are shown |
| Turn off Wi-Fi / hotspot | App shows "Could not load departures" and keeps running |
| Select a stop with å, ä or ö | Characters are shown correctly |