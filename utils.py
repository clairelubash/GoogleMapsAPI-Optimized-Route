from datetime import datetime
import pandas as pd
from itertools import product


def get_lat_long(gmaps, address):
    """gets latitude and longitude values from an address

    Arguments:
        address (str): address for the desired coordinates

    Returns:
        lat, long (float): latitude and longitude of given address
    """

    geocode_result = gmaps.geocode(address)
    lat, long = geocode_result[0]['geometry']['location'].values()

    return lat, long



def closest_from_keyword(gmaps, keyword, latitude, longitude, k = None):
    """pulls k closest places to lat/long based on keyword for the place 
    (e.g. keyword = 'Target' pulls the closest Target stores to the coordinates)

    Args:
        keyword (str): keyword used to describe type of place the user is looking for
        latitude (float): latitude of starting location 
        longitude (float): longitude of starting location
        k (int, optional): number of places to return. Defaults to None.

    Returns:
        filtered_places_lst (list): list of dictionaries with address and lat/long for each of the nearby places
    """

    closest_places = gmaps.places(query = keyword, location = {'lat': latitude, 'lng': longitude})

    filtered_places_lst = []
    unique_global_codes = set()

    if k:

        for i in closest_places['results'][:k]:

            curr_global_code = i['plus_code']['global_code']

            if curr_global_code not in unique_global_codes:
                places_dict = {}

                places_dict['latitude'] = i['geometry']['location']['lat']
                places_dict['longitude'] = i['geometry']['location']['lng']

                filtered_places_lst.append(places_dict)
                unique_global_codes.add(curr_global_code)

    return filtered_places_lst



def convert_to_minutes(time_str):
    """converts duration output from directions api to a single value in minutes

    Args:
        time_str (str): duration output from directions api

    Returns:
        total_minutes (int): duration in minutes
    """

    parts = time_str.split()
    total_minutes = 0

    for i in range(0, len(parts), 2):
        value = int(parts[i])
        unit = parts[i + 1].lower()

        if unit.startswith('hour'):
            total_minutes += value * 60
        elif unit.startswith('min'):
            total_minutes += value

    return total_minutes



def get_route_duration(gmaps, start_end_address, waypoints):
    """gets total driving time from starting point to ending point through all waypoints

    Args:
        start_end_address (tuple): longitude and latitude of starting/ending address
        waypoints (list): list of longitude and latitude of every waypoint

    Returns:
        total_duration (int): total driving time through all waypoints
    """

    now = datetime.now()

    dirs = gmaps.directions(start_end_address, 
                            start_end_address, 
                            waypoints = waypoints, 
                            optimize_waypoints = True, 
                            mode = 'driving', 
                            departure_time = now,
                            )

    total_duration = 0

    for i in range(len(dirs[0]['legs'])):
        total_duration += convert_to_minutes(dirs[0]['legs'][i]['duration']['text'])

    return total_duration




def create_waypoint_combo_df(list_of_lists):
    """create dataframe of waypoint coordinate combinations

    Args:
        list_of_lists (list): a list for each waypoint containing the coordinates of the closest locations

    Returns:
        df (pandas df): dataframe of waypoints coordinates
    """

    # coordinates = []
    # for lst in list_of_lists:
    #     latitudes = [d['latitude'] for d in lst]
    #     longitudes = [d['longitude'] for d in lst]
    #     coordinates.append((latitudes, longitudes))

    # combinations = [list(zip(*coords)) for coords in product(*coordinates)]

    # df = pd.DataFrame({'waypoints': combinations})

    combinations = list(product(*list_of_lists))
    pairs = [[(item[i]['latitude'], item[i]['longitude']) for i in range(len(list_of_lists))] for item in combinations]
    df = pd.DataFrame({'waypoints': pairs})

    return df
