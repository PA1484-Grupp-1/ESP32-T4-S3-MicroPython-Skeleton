# Development

This guide explains how to develop/configure the ESP32 project. It focuses on Trafiklab API used to show public transport departures.

# Setup

1. Open the project in VS
2. Run project/create_secrets.bat to create secrets_env.py
3. Add your wifi credentials and trafiklab API key. 
4. Connect the ESP32 board.  


# Trafiklab API
The project uses the APIs to query information. 

Trafiklab Realtime API to get public transport departures.

("https://realtime-api.trafiklab.se/v1/departures/"
    "{STOP_GROUP_ID}?key={API_KEY}")

Replace {STOP_GROUP_ID} and {API_KEY} with your values.

The API returns depature times, delays, destination, and transport types. Stop IDs are listed in project/stations.py

ResRobot Trafiklab API to get the best journey between two stations.

("https://api.resrobot.se/v2.1/trip?format=json"
    "&originId={FROM_STOP_GROUP_ID}&destId={TO_STOP_GROUP_ID}"
    "&lang=en&numF=1&accessId={API_KEY}")

Replace {FROM_STOP_GROUP_ID}, {TO_STOP_GROUP_ID} and {API_KEY} with your values.

The API returns journey legs/steps on how to perform the journey. Each step has a step type, origin, destination, line, departure and arrival time.

# API Documentation
- Trafiklab Realtime API: 
https://www.trafiklab.se/api/our-apis/trafiklab-realtime-apis/

- ResRobot Trafiklab API
https://www.trafiklab.se/api/our-apis/resrobot-v21/

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
| Swipe down/right/left (US2.1, US3.1, US5.1) | Moves between start, departures, journey and settings screens |
| Open departures (US1.2B) | Line, destination, time and status are shown for the selected stop |
| Click on the stop search area | Text gets cleared and suggestions dropdown and keyboard appears |
| Start searching for a stop (US3.2C) | The suggested stops are updated and contains the search string |
| Unfocusing the stop search area | Displays the selected stations name and hides the suggested dropdown and keyboard |
| Select another stop (US3.2C) | Departure table changes to the new stop |
| Select Bus/Train/Ferry/All (US3.3) | Only the selected transport type is shown |
| Save Default, restart the device (US3.4) | Saved stop and transport type are restored |
| Change settings, press Reset to Default (US3.5) | Settings go back to the saved default |
| Wait 60 seconds (US4.1) | Departure table updates by itself |
| Press the refresh button (US4.2) | Departure table updates |
| Open settings (US4.3) | Wi-Fi and live data status are shown |
| Turn off Wi-Fi / hotspot | App shows "Could not load departures" and keeps running |
| Select a stop with å, ä or ö | Characters are shown correctly |
| Click on a "From" or "To" stop search area | Shows the suggestion dropdown and keyboard |
| Start searching for a "From" or "To" stop (US5.2B) | The suggested stops are updated and contains the search string |
| Unfocusing the "From" or "To" stop search area | Hides the suggested dropdown and keyboard |
| Select both a "From" and "To" stop (US5.3B) | Journey instructions shows the departure time for each intermediate stop and where to change transportation |
| Press the journey refresh button | Journey instructions updates |
| Selecting a suggested dropdown option when searching a stop | Sets the stop as the selected stop and hides the suggested dropdown and keyboard |
| Pressing the up arrow on the keyboard | Switches between upper- and lowercase |
| Pressing the X button on the keyboard | Clears the input text |
| Pressing the checkmark on the keyboard | Hides the keyboard |
| Pressing the textarea while the keyboard is hidden by clicking on the checkmark | Shows the keyboard |