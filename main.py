import googlemaps
import os
from dotenv import load_dotenv
from utils import *

load_dotenv()


gmaps = googlemaps.Client(key = os.getenv('MAPS_API_KEY'))


starting_ending_address = '122 Morris St Morristown NJ'
start_lat, start_long = get_lat_long(gmaps, starting_ending_address)
start_coords = (start_lat, start_long)

keyword_lst = ['Target', 'DSW']
k = 3

lst_of_lsts = []

for key in keyword_lst:
    places_lst = closest_from_keyword(gmaps, key, start_lat, start_long, k = k)
    lst_of_lsts.append(places_lst)

df = create_waypoint_combo_df(lst_of_lsts)

df['duration'] = df['waypoints'].apply(lambda x: get_route_duration(gmaps, start_coords, x))

min_duration = df['duration'].min()
best_waypoints = df.loc[df['duration'] == min_duration, 'waypoints'].tolist()

optimized_route = [start_coords] + best_waypoints[0] + [start_coords]








