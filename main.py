import googlemaps
import os
from dotenv import load_dotenv
from utils import *
from flask import Flask, request, render_template
import folium

load_dotenv()


app = Flask(__name__)


def get_optimized_route(starting_ending_address, keyword_lst, k = 3):

    gmaps = googlemaps.Client(key = os.getenv('MAPS_API_KEY'))

    start_lat, start_long = get_lat_long(gmaps, starting_ending_address)
    start_coords = (start_lat, start_long)

    lst_of_lsts = []

    for key in keyword_lst:
        places_lst = closest_from_keyword(gmaps, key, start_lat, start_long, k = k)
        lst_of_lsts.append(places_lst)

    df = create_waypoint_combo_df(lst_of_lsts)

    df['duration'] = df['waypoints'].apply(lambda x: get_route_duration(gmaps, start_coords, x))

    min_duration = df['duration'].min()
    best_waypoints = df.loc[df['duration'] == min_duration, 'waypoints'].tolist()
    best_waypoints_add = df.loc[df['duration'] == min_duration, 'addresses'].tolist()
    best_waypoints_names = df.loc[df['duration'] == min_duration, 'names'].tolist()

    optimized_route = [start_coords] + best_waypoints[0] + [start_coords]

    optimized_route_dict = {'origin': {'coordinates': start_coords, 'address': starting_ending_address, 'name': 'Origin & Destination'}}

    for idx, coord_pair in enumerate(optimized_route[1:-1]):
        stop_num = f'Stop #{idx+1}'.format()

        if stop_num not in optimized_route_dict:
            optimized_route_dict[stop_num] = {}

        optimized_route_dict[stop_num]['coordinates'] = coord_pair
        optimized_route_dict[stop_num]['address'] = best_waypoints_add[0][idx][0]
        optimized_route_dict[stop_num]['name'] = best_waypoints_names[0][idx][0]

    optimized_route_dict['destination'] = {'coordinates': start_coords, 'address': starting_ending_address, 'name': 'Origin & Destination'}

    return optimized_route_dict


def generate_map(coordinates_dict):

    coordinates = [sub_dict['coordinates'] for sub_dict in coordinates_dict.values() if 'coordinates' in sub_dict]

    map = folium.Map(location = coordinates[0], zoom_start = 12)

    for i in range(len(coordinates_dict)):
        location = coordinates[i]
        if 'address' in list(coordinates_dict.values())[i]:
            add_value = list(coordinates_dict.values())[i]['address']
        if 'name' in list(coordinates_dict.values())[i]:
            name_value = list(coordinates_dict.values())[i]['name']
        if i == 0 or i == (len(coordinates) - 1):
            tag = name_value + '\n' + add_value
        else:
            tag = f'Stop #{i}:'.format() + '\n' + name_value + '\n' + add_value
        folium.Marker(location, popup = tag).add_to(map)

    return map


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':

        param1 = str(request.form['param1'])
        param2 = [x.strip() for x in request.form['param2'].split(',')]
        
        result = get_optimized_route(param1, param2)

        generated_map = generate_map(result)

        map_file = "templates/map.html"
        generated_map.save(map_file)

        return render_template('index.html')

    return render_template('input.html')



if __name__ == '__main__':
    app.run(debug=True)



