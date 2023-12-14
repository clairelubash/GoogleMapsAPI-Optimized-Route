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

    optimized_route = [start_coords] + best_waypoints[0] + [start_coords]

    return optimized_route


def generate_map(coordinates):
    map = folium.Map(location = coordinates[0], zoom_start = 12)
    for i in range(len(coordinates)):
        location = coordinates[i]
        if i == 0 or i == (len(coordinates) - 1):
            tag = 'Origin & Destination'
        else:
            tag = f'Stop #{i}'.format()
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



