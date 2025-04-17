import os
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import polyline

# init geocoder with user agent
geolocator = Nominatim(user_agent="eld_planner_app")

MAPBOX_ACCESS_TOKEN = os.environ.get('MAPBOX_ACCESS_TOKEN', 'pk.sample_key')

def geocode_location(location_str):
    # converting a location string using longitude and latitude
    try:
        location = geolocator.geocode(location_str)
        if location:
            return {
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        else:
            raise ValueError(f"Could not geocode location: {location_str}")
    except Exception as e:
        raise Exception(f"Geocoding error: {str(e)}")

def calculate_distance(point1, point2):
    # calculate distance between two points in a mile
    # geopy reference i used https://geopy.readthedocs.io/en/stable/index.html?highlight=geodesic#geopy.distance.geodesic
    return geodesic(
        (point1["latitude"], point1["longitude"]),
        (point2["latitude"], point2["longitude"])
    ).miles

def fetch_route(origin, destination):
    # fetch data from mapbox api
    try:
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origin['longitude']},{origin['latitude']};{destination['longitude']},{destination['latitude']}"
        params = {
            "access_token": MAPBOX_ACCESS_TOKEN,
            "geometries": "geojson",
            "overview": "full",
            "steps": "true"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if "routes" not in data or not data["routes"]:
            raise ValueError("No routes found")

        route = data["routes"][0]

        return {
            "distance": route["distance"] * 0.000621371,  # meters to miles
            "duration": route["duration"] / 60 / 60,  # seconds to hours
            "geometry": route["geometry"],
            "steps": route["legs"][0]["steps"] if route["legs"] else []
        }
    except Exception as e:
        # for demo, if api fails just estimate data
        print("API FAILED - ESTIMATING DATA")
        distance = calculate_distance(origin, destination)
        return {
            "distance": distance,
            "duration": distance / 55,  # traveling at a rate of 55mph
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [origin["longitude"], origin["latitude"]],
                    [destination["longitude"], destination["latitude"]]
                ]
            },
            "steps": []
        }

def plan_route(current_location, pickup_location, dropoff_location):
    # plan for a complete route including fuel stops

    # geocode locations
    current_coords = geocode_location(current_location)
    pickup_coords = geocode_location(pickup_location)
    dropoff_coords = geocode_location(dropoff_location)

    # fetching routes for each segment
    to_pickup_route = fetch_route(current_coords, pickup_coords)
    delivery_route = fetch_route(pickup_coords, dropoff_coords)

    # calculate total distance and duration
    total_distance = to_pickup_route["distance"] + delivery_route["distance"]
    total_duration = to_pickup_route["duration"] + delivery_route["duration"]

    # incrememt 1 hr / pickup and dropoff
    pickup_duration = 1.0
    dropoff_duration = 1.0

    total_driving_duration = total_duration
    total_duration += pickup_duration + dropoff_duration

    # determine fuel stops every 1000 miles
    num_fuel_stops = int(total_distance / 1000)
    fuel_stops = []

    if num_fuel_stops > 0:
        # spread out fuel stops evenly
        distance_between_stops = total_distance / (num_fuel_stops + 1)

        accumulated_distance = 0
        current_point = current_coords

        segments = [
            {"route": to_pickup_route, "end": pickup_coords},
            {"route": delivery_route, "end": dropoff_coords}
        ]

        for segment in segments:
            segment_distance = segment["route"]["distance"]

            while accumulated_distance + distance_between_stops <= total_distance and len(fuel_stops) < num_fuel_stops:
                next_stop_distance = distance_between_stops - (accumulated_distance % distance_between_stops)

                if next_stop_distance < segment_distance:
                    # add fuel stop within segment, for this assessment i just estimate
                    stop_ratio = next_stop_distance / segment_distance
                    fuel_stop = {
                        "type": "fuel",
                        "distance_from_start": accumulated_distance + next_stop_distance,
                        "estimated_location": f"Along route to {segment['end']['address']}",
                        "duration": 0.5  # 30 mins
                    }
                    fuel_stops.append(fuel_stop)
                    total_duration += fuel_stop["duration"]
                    accumulated_distance += next_stop_distance
                else:
                    # stop is in the next segment
                    break

            accumulated_distance += segment_distance

    # summation of route data
    route_data = {
        "segments": [
            {
                "from": current_coords,
                "to": pickup_coords,
                "distance": to_pickup_route["distance"],
                "duration": to_pickup_route["duration"],
                "geometry": to_pickup_route["geometry"]
            },
            {
                "from": pickup_coords,
                "to": dropoff_coords,
                "distance": delivery_route["distance"],
                "duration": delivery_route["duration"],
                "geometry": delivery_route["geometry"]
            }
        ],
        "stops": [
            {
                "type": "pickup",
                "location": pickup_coords,
                "duration": pickup_duration
            },
            {
                "type": "dropoff",
                "location": dropoff_coords,
                "duration": dropoff_duration
            }
        ],
        "fuel_stops": fuel_stops,
        "total_distance": total_distance,
        "total_driving_duration": total_driving_duration,
        "total_duration": total_duration
    }

    return route_data