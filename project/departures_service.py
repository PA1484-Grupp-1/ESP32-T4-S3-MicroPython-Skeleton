import requests

from secrets_env import TRAFIKLAB_API_KEY, RESROBOT_API_KEY


def within_target(lat, lon) -> bool:
    raise NotImplementedError()

# Only used on a PC to generate stations.py


def query_all_stop_groups() -> list:
    GET_STOPS_URL = ("https://realtime-api.trafiklab.se/v1/stops/list"
                     "?key={API_KEY}")

    result: requests.Response = requests.get(
        GET_STOPS_URL.format(API_KEY=TRAFIKLAB_API_KEY))

    body = result.json()

    stop_groups = []
    for stop_group in body["stop_groups"]:

        if stop_group["area_type"] != "RIKSHALLPLATS":
            continue

        for stop in stop_group["stops"]:
            if within_target(float(stop["lat"]), float(stop["lon"])):
                stop_groups.append(stop_group)
                break

    return stop_groups

# US1.2B: Live departures from the Trafiklab Realtime API


def query_departures(stop_group_id: str) -> list:
    GET_DEPARTURES_URL = ("https://realtime-api.trafiklab.se/v1/departures/"
                          "{STOP_GROUP_ID}?key={API_KEY}")
    
    try:
        result: requests.Response = requests.get(GET_DEPARTURES_URL.format(
            STOP_GROUP_ID=stop_group_id, API_KEY=TRAFIKLAB_API_KEY), timeout=1.5)
        
        return result.json()["departures"]
    finally:
        # Frees the socket, needed for the auto refresh (US4.1)
        result.close()


def query_journeys(from_stop_group_id: str, to_stop_group_id: str) -> list:
    GET_JOURNEY_URL = ("https://api.resrobot.se/v2.1/trip?format=json"
                       "&originId={FROM_STOP_GROUP_ID}&destId={TO_STOP_GROUP_ID}"
                       "&lang=en&numF=1&accessId={API_KEY}")

    try:
        result: requests.Response = requests.get(GET_JOURNEY_URL.format(
            FROM_STOP_GROUP_ID=from_stop_group_id, TO_STOP_GROUP_ID=to_stop_group_id,
            API_KEY=RESROBOT_API_KEY), timeout=1.5)

        return result.json()["Trip"]
    finally:
        result.close()