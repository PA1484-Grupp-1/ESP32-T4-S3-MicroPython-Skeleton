## Introduction
This part should give a general introduction to your project. Briefly describe your project:
- What the system does
- What problem it solves
- What technologies it uses (ESP32, touchscreen, API, PlatformIO)
- What the main functionality is

## Getting started
This section should guide a new developer through the steps of how to set up theproject and install the dependencies they need to start developing.
It can include: 

## Building and running
This is where you explain how to make the project run.

Examples of things to describe:
- How to build/upload the program to the ESP32
- What your startup procedure looks like
- If the program accepts different arguments or modes
- How to operate the program (e.g., touchscreen interaction)

## Features
Lastly, write which of the user stories you did and didn't develop in this project, in the form of a checklist. Like this:

- [x] US1.1: As a user, I want to see a starting screen displaying the project name, current program version, group number, and members' names.
- [x] US1.2: As a user, I want to see a departure screen showing demo public transport departure data for Campus Gräsvik and Karlskrona Centralstation.
- [x] US1.2A: As a user, I want to see the departure screen showing demo departure data: departure time, line, destination, and departure status for five destinations in Karlskrona, including Campus Gräsvik and Karlskrona Centralstation.
- [x] US1.2B: As a user, I want to see the departure screen showing departure data: departure time, line, destination, and departure status for any destinations in Karlskrona using live data from Trafiklab
- [x] US2.1: As a user, I want to navigate between different screens by sliding a finger over the touchscreen.
- [x] US3.1: As a user, I want to access a settings screen.
- [x] US3.2: As a user, I want to select different stops from US1.2.
- [x] US3.2A: As a user, I want to select different stops from US1.2A.
- [x] US3.2B: As a user, I want to select different stops from US1.2B.
- [x] US3.2C: As a user, I want to search and select different stops for US1.2B.
- [x] US3.3: As a user, I want to select a transport type (bus, train, ferry, and all) using a dropdown.
- [x] US3.4: As a user, I want to save my current settings as the default and have them restored when the device restarts.
- [x] US3.5: As a user, I want to reset my current settings to the stored default settings. 
- [x] US4.1: As a user, I want the live departure data to update automatically in 60 seconds.
- [x] US4.2: As a user, I want to manually refresh the departure data. 
- [x] US4.2B: As a user, I want to manually refresh the departure data with a button in the settings screen.
- [x] US4.3: As a user, I want to see the current Wi-Fi connection and live data status on the settings screen. 
- [x] US5.1: As a user, I want to access a journey selection screen.
- [x] US5.2B: As a user, I want to search for and select a starting stop and a final destination stop for US5.3.
- [x] US5.3B: As a user, I want to see the top matching journey, based on arrival time to the final destination, that shows the departure time for each intermediate stop where I must change transportation.

### Not Planned
User Stories not started and overwritten by later User Stories.

- US5.3: **(Overwritten by US5.3B)** As a user, I want to see the top 5 matching journeys that show the departure time for each intermediate stop where I must change transportation.
- US5.2: **(Overwritten by US5.2B)** As a user, I want to select a starting stop and a final destination stop. 


