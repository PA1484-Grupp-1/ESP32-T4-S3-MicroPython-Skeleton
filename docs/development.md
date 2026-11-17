# Development

This guide explains how to develop/configure the ESP32 project. It focuses on Trafiklab API used to show public transport departures.

# Setup

1. Open the project in VS
2. Run project/create_secrets.bat to create secretes_env.py
3. Add your wife credentials and trafiklab API key. 
4. Connect the ESP32 board.  


# Trafiklab API

The project uses the Trafiklab Realtime API to get public transport departures.

("https://realtime-api.trafiklab.se/v1/departures/"
                          "{STOP_GROUP_ID}?key={API_KEY}")

{Replace STOP_GROUP_ID} and {API_KEY} with your values.

The API returns depature times, delays, destination, and transport types. Stop IDs are listed in project/stations.py

# API Documentation
- Trafiklab Realtime API: 
https://www.trafiklab.se/api/our-apis/trafiklab-realtime-apis/