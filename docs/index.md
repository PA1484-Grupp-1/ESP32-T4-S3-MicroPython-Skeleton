# Introduction

This project is based on the ESP32-T4-S3 LilyGO board. It uses MicroPython and LVGL to develop applications with a graphical user interface.

The original template has been extended with a bus departure application that displays real-time public transport information. 

# Documentation 
    - README.md - Project introduction, installation and setup instructions.
    - UPLOAD.md - Introductions on how to upload.
    - TYPINGS.md - Instructions for setting up LVGL code completion.  
    - index.md - The main documentation file and guides users to its content.
    - development.md - Describes the development process, including APIs.
    - hardware.md - Describes the hardware components.
    - software.md - Describes the software components.
    - troubleshooting.md - A guide covering common technical issuess and how to solve them.

# Project Structure
    - .typings/ - Contains type definitions for code completion.
    - assets/ - Contains project image.
    - boards/ - Contains board configurations files.
    - docs/ - Contains project documentation, guides and instructions.
    - firmware/ - Contains the MicroPython firmware and LVGL
    - platformio/ - Contains scripts for building and uploading the project.
    - project/ - Contains the Python application code.
    - support/ - Contains hardware, drivers and startup files.

# Data Attribution
Public transport data is provided by [Trafiklab](https://www.trafiklab.se/) through the Trafiklab Realtime API. The app shows "Data: Trafiklab.se" on the departure screen.