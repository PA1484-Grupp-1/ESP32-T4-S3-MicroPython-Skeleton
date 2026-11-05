import requests

from secrets_env import TRAFIKLAB_API_KEY

TARGET_LOCATION = (56.18684333961802, 15.61205558484464) # Middle of Karlskrona
MAX_DISTANCE = 0.05

def within_target(lat, lon) -> bool:
    return ((lat - TARGET_LOCATION[0])**2 + (lon - TARGET_LOCATION[1])**2) <= (MAX_DISTANCE * MAX_DISTANCE)

# PC-only: regenerates stations.py (see below). Never called on the device.
def query_all_stop_groups() -> list:
    GET_STOPS_URL = "https://realtime-api.trafiklab.se/v1/stops/list?key={API_KEY}"

    result: requests.Response = requests.get(GET_STOPS_URL.format(API_KEY=TRAFIKLAB_API_KEY))

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

def query_departures(stop_group_id: str) -> list:
    GET_DEPARTURES_URL = "https://realtime-api.trafiklab.se/v1/departures/{STOP_GROUP_ID}?key={API_KEY}"

    result: requests.Response = requests.get(GET_DEPARTURES_URL.format(STOP_GROUP_ID=stop_group_id, API_KEY=TRAFIKLAB_API_KEY))
    
    body = result.json()
    
    return body["departures"]

#if __name__ == "__main__":
#    stop_groups = query_all_stop_groups()
#    export_stops = ["\t[ \"" + stop_group["id"] + "\", \"" + stop_group["stops"][0]["name"] + "\" ]," for stop_group in stop_groups]
#    joined = "\n".join(export_stops)[:-1]
#    with open("project/stations.py", "w", encoding="UTF8") as f:
#        f.write(f"stations = [\n{joined}\n]")
