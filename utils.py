from datetime import datetime
import pandas as pd
from itertools import product
import folium
import googlemaps
import os


def get_lat_long(gmaps, address):
    """gets latitude and longitude values from an address using geocode api

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

    closest_places = gmaps.places(query = keyword, 
                                  location = {
                                      'lat': latitude, 
                                      'lng': longitude
                                      }
                                )

    filtered_places_lst = []
    unique_global_codes = set()

    if k:
        places_to_process = closest_places['results'][:k]

        filtered_places_lst = [
            {
                'latitude': place['geometry']['location']['lat'],
                'longitude': place['geometry']['location']['lng'],
                'address': place['formatted_address'],
                'name': place['name']
            }
            for place in places_to_process if (curr_global_code := place['plus_code']['global_code']) not in unique_global_codes and not unique_global_codes.add(curr_global_code)
        ]

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

    for value, unit in zip(parts[::2], parts[1::2]):
        value = int(value)
        unit = unit.lower()

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

    leg_durations = [convert_to_minutes(leg['duration']['text']) for leg in dirs[0]['legs']]
    total_duration = sum(leg_durations)

    return dirs, total_duration



def create_waypoint_combo_df(list_of_lists):
    """create dataframe of waypoint coordinate combinations

    Args:
        list_of_lists (list): a list for each waypoint containing the coordinates of the closest locations

    Returns:
        df (pandas df): dataframe of waypoints coordinates
    """

    combinations = list(product(*list_of_lists))

    pairs = [[(item['latitude'], item['longitude']) for item in combo] for combo in combinations]
    addresses = [[(item['address'],) for item in combo] for combo in combinations]
    names = [[(item['name'],) for item in combo] for combo in combinations]

    df = pd.DataFrame({'waypoints': pairs, 'addresses': addresses, 'names': names})

    return df



def get_optimized_route(starting_ending_address, keyword_lst, k = 3):

    """calls the places api to get the best waypoints for minimized driving time

    Args:
        starting_ending_address (str): starting point for user
        keyword_lst (list): list of waypoints the user chose
        k (int, optional): number of places to return. Defaults to 3.

    Returns:
        optimized_route_dict (dictionary): dictionary of coords and names for optimized places
        dirs[0][0]["legs"] (dictionary): portion of dict describing the legs of journey with directions
        min_duration (int): minimum driving time possible with waypoints
    """

    gmaps = googlemaps.Client(key = os.getenv('MAPS_API_KEY'))

    start_lat, start_long = get_lat_long(gmaps, starting_ending_address)
    start_coords = (start_lat, start_long)

    lst_of_lsts = [closest_from_keyword(gmaps, key, start_lat, start_long, k = k) for key in keyword_lst]

    df = create_waypoint_combo_df(lst_of_lsts)

    df['duration'] = df['waypoints'].apply(lambda x: get_route_duration(gmaps, start_coords, x)[1])

    min_duration = df['duration'].min()
    best_waypoints = df.loc[df['duration'] == min_duration]

    optimized_route = [start_coords] + best_waypoints['waypoints'].iloc[0] + [start_coords]

    optimized_route_dict = {
        'origin': {'coordinates': start_coords, 
                   'address': starting_ending_address, 
                   'name': 'Origin & Destination'}
        }

    for idx, coord_pair in enumerate(optimized_route[1:-1]):
        stop_num = f'Stop #{idx+1}'
        optimized_route_dict.setdefault(stop_num, {})
        optimized_route_dict[stop_num]['coordinates'] = coord_pair
        optimized_route_dict[stop_num]['address'] = best_waypoints['addresses'].iloc[0][idx][0]
        optimized_route_dict[stop_num]['name'] = best_waypoints['names'].iloc[0][idx][0]

    optimized_route_dict['destination'] = {
        'coordinates': start_coords,
        'address': starting_ending_address,
        'name': 'Origin & Destination'
        }

    dirs = get_route_duration(gmaps, start_coords, optimized_route)

    return optimized_route_dict, dirs[0][0]['legs'], min_duration



def generate_map(coordinates_dict):

    """creates folium map from route coordinates

    Args:
        coordinates_dict (dictionary): mapping of stops and their coordinates

    Returns:
        map: folium map for UI
    """

    coordinates = [sub_dict['coordinates'] for sub_dict in coordinates_dict.values() if 'coordinates' in sub_dict]

    map = folium.Map(location = coordinates[0], zoom_start = 12)

    for i, (key, sub_dict) in enumerate(coordinates_dict.items()):
        location = sub_dict.get('coordinates')
        add_value = sub_dict.get('address', '')
        name_value = sub_dict.get('name', '')

        if i == 0 or i == len(coordinates_dict) - 1:
            tag = f"<b>{name_value}:</b><br/>{add_value}" if name_value else add_value
            icon = folium.Icon(icon = 'home',
                               prefix = 'fa',
                               color = 'red',
                               )
        else:
            tag = f"<b>Stop #{i}:</b> {name_value}<br/><b>Address:</b> {add_value}" if name_value else f"<b>Stop #{i}:</b><br/>{add_value}"
            icon = None

        folium.Marker(location,
                      popup = folium.Popup(tag, parse_html = False, max_width = 500), 
                      icon = icon
                      ).add_to(map)
        
    folium.PolyLine(coordinates, 
                    weight = 5, 
                    opacity = 1
                    ).add_to(map)

    return map



def format_instructions(directions_dict):

    """grabs all instructions and combines them into one string for UI

    Args:
        directions_dict (dictionary): dictionary of directions pulled from directions api

    Returns:
        html_instructions_combined (str): directions output for UI
    """

    html_instructions_combined = ''.join(step.get('html_instructions', '') + '\n' for element in directions_dict for step in element.get('steps', []))
    
    return html_instructions_combined
