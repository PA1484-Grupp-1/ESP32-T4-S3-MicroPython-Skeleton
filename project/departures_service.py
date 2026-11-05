import requests

from secrets_env import TRAFIKLAB_API_KEY

TARGET_LOCATION = (56.18684333961802, 15.61205558484464) # Middle of Karlskrona
MAX_DISTANCE = 0.05

def within_target(lat, lon) -> bool:
    return ((lat - TARGET_LOCATION[0])**2 + (lon - TARGET_LOCATION[1])**2) <= (MAX_DISTANCE * MAX_DISTANCE)

def query_all_stop_groups() -> list:
    GET_STOPS_URL = "https://realtime-api.trafiklab.se/v1/stops/list?key={API_KEY}"

    try:
        result: requests.Response = requests.get(GET_STOPS_URL.format(API_KEY=TRAFIKLAB_API_KEY), timeout=4.5)
        if not result.ok:
            return []

        body = result.json()

        # Filter stop groups close to target
        stop_groups = []
        for stop_group in body["stop_groups"]:

            if stop_group["area_type"] != "RIKSHALLPLATS":
                continue

            for stop in stop_group["stops"]:
                if within_target(float(stop["lat"]), float(stop["lon"])):
                    stop_groups.append(stop_group)
                    break

        return stop_groups
    except TimeoutError:
        return []

def query_departures(stop_group_id: str) -> list:
    GET_DEPARTURES_URL = "https://realtime-api.trafiklab.se/v1/departures/{STOP_GROUP_ID}?key={API_KEY}"

    try:
        result: requests.Response = requests.get(GET_DEPARTURES_URL.format(STOP_GROUP_ID=stop_group_id, API_KEY=TRAFIKLAB_API_KEY), timeout=4.5)
        if not result.ok:
            return []

        body = result.json()

        return body["departures"]
    
    except TimeoutError:
        return []