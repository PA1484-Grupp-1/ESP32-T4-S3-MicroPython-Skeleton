## Introduction

This project is based on the ESP32-T4-S3 LilyGO board. It uses MicroPython and LVGL to develop applications with a graphical user interface. The original template repository has been extended with a bus departure application that displays real-time public transport information. It uses Trafiklab Realtime API to get public transport departures data.

This solution aims to provide users with a seamless and intuitive way to navigate Karlskrona's public transport network, making journey planning and accessing travel information easier and more effecient. 

*For more detailed information about the project's development, see [docs/index.md](./docs/index.md)*

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

## Building and running
### how to upload to ESP32
To upload to the ESP32, Hold down Boot and the press RST to go into upload mode. Open PlatformIO extension tab, Project Tasks > t4s3-micropython > Custom then wait for the loading bar to finish, then build python application and flash project application. Finally hold RST for 3 seconds to start the application.

### what is start-up procedure 
To start the device it needs to be connected by USB-C to a computer and connected by WiFi. Once connected the device starts automatically. If the device is not connected to WiFi it will still turn on but the display will not turn on.
if the program accepts different arguments

### Arguments

### How to operate
To operate, the device needs to be connected to a computer and WiFi, turn on the device and swipe down to bring up the departures menu. To change the stations, swipe left then press on the station tab you want to change (To and from) press on the station and a drop down list of different stations will appear. If you want to save the stations as default you press the button and those stations will become the default ones. If you wish to reload the departures list there is a button to do it manually.

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


