# Software

Explain how the project's software is structured and how it works.

# Main Application



# API Communication - project\departures_service.py

Communicates with the Trafiklab API using HTTP GET requests. The API key is loaded from secrete_env.py

- **query_depature()**: Retrieves depatures for a specific stop ID.
- **within_target()**: Checks geographical coordinates.
- **query_all_stop_groups()**: Retrieves stop groups used to generate the station list.


# Departure Board - project\departure_list.py

Creates and updates the departure board using LVGL objects. It also handles text fields, colors and and status messages.

Conatins two classes.

- **Departureboard**: Manages the complete board.
- **DepartureRow**: Represents an individual departure.


# Station Data - project\stations.py

Contains a list of stations. Each entry consists of a station ID and a name. This data is used to populate the station dropdown menu. 


# UI Styling - project\styles.py

Define colors, fonts, and reusable visual styles. The **init_fonts()** function loads the projects additional fonts.