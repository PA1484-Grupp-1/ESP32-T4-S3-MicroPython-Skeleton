# Software

Explain how the project's software is structured and how it works.

# Main Application - project\main.py

Creates the user interface and connects all modules.

- **Start screen** (US1.1): Project name, version, group and members.
- **Departure screen** (US1.2B): The stop name as title, with the selected transport type below it (e.g. "Departures · Train", US3.3). Table with line (bus line or train number), destination, time and status (On time, +N min or Cancelled). Text that is too long for a cell ends with "...". Has a refresh button (US4.2) and Trafiklab attribution.
- **Journey screen** (US5.1 - US5.3): Select departure and destination stop, travel instructions are displayed for the journey. Each step in the journey has departure time for each intermediate stop where one must change transportation. Has a refresh button and ResRobot Trafiklab attribution
- **Settings screen** (US3.1 - US3.5): Stop and transport type (All, Bus, Train, Ferry), Save Default, Reset to Default, and live data status (US4.3).
- **Wi-Fi icon** (US4.3): Phone-style icon in the top right corner of every screen (on LVGL's top layer). White when connected, grey when not.
- **Auto refresh** (US4.1): An LVGL timer updates the departures every 60 seconds.
- **Error handling**: All callbacks are wrapped with `safe()`, so an error is logged instead of crashing the device.


# API Communication - project\departures_service.py

Communicates with the Trafiklab API using HTTP GET requests. The API key is loaded from `secrets_env.py`

- **query_departures()**: Retrieves depatures for a specific stop ID.
- **query_journeys()**: Retrieves instructions on how to travel between two specific stop IDs.
- **within_target()**: Checks geographical coordinates.
- **query_all_stop_groups()**: Retrieves stop groups used to generate the station list.


# Keyboard Implementation - project\custom_keyboard.py

Custom keyboard implementation that has all letters that the stations use.


# Search Area - project\search_area.py

Custom widget handling searching for options.


# User Settings - project\user_settings.py

Saves and loads the selected stop and transport type in settings.json on the device.


# Station Data - project\stations.py

Contains a list of stations. Each entry consists of a station ID and a name. This data is used to populate the station dropdown menu. 


# UI Styling - project\styles.py

Define colors, fonts, and reusable visual styles. The fonts are loaded from **fonts.py**.


# Formatting - project\format_helpers.py

Helper functions for formatting.


# Fonts - project\fonts.py

The built-in LVGL fonts only contain ASCII. fonts.py contains the letters Å Ä Ö Æ Ø É Ü å ä ö æ ø é ü as data (only capitals for the 28 px title font) (rendered once from the same Montserrat font) and builds an LVGL font from them in **load()**, which is called after the board has started. All other characters and symbols come from the built-in font (fallback). If something fails, the built-in fonts are used.

# User Story Overview

The code comments refer to the user stories (US#) and requirements (NF#) they implement.

| Story | Where |
| --- | --- |
| US1.1 Start screen | main.py, `create_ui()` |
| US1.2B Departures with live data | main.py, `update_departure_table()`, departures_service.py, `query_departures()` |
| US2.1 Swipe navigation | main.py, tileview in `create_ui()` |
| US3.1 Settings screen | main.py, `create_ui()` |
| US3.2B Select stop | main.py, `on_stop_changed()`, stations.py |
| US3.3 Select transport type | main.py, `on_transport_changed()` and the filter in `update_departure_table()` |
| US3.4 Save default settings | main.py, `on_save_clicked()`, user_settings.py |
| US3.5 Reset to default settings | main.py, `on_reset_clicked()`, user_settings.py |
| US4.1 Auto refresh every 60 s | main.py, `refresh_timer` |
| US4.2 Manual refresh | main.py, Refresh button |
| US4.3 Wi-Fi and live data status | main.py, `create_wifi_icon()`, `update_wifi_icon()`, `lbl_live` |
| NF3 Trafiklab attribution | main.py, `lbl_attribution` |