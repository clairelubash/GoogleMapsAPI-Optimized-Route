from dotenv import load_dotenv
from utils import *
from flask import Flask, request, render_template, session, redirect, url_for



app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':

        param1 = str(request.form['param1'])
        param2 = [x.strip() for x in request.form['param2'].split(',')]
        
        result, dirs, total_duration = get_optimized_route(param1, param2)

        formatted_dirs = format_instructions(dirs)
        session['formatted_dirs'] = formatted_dirs
        formatted_duration = str(total_duration) + ' minutes'

        itinerary = '\n\n'.join(f"{key.capitalize() if key in ['origin', 'destination'] else value['name'].split(':')[0]}: {value['address'].title()}" for key, value in result.items())

        generated_map = generate_map(result)

        map_file = "templates/map.html"
        generated_map.save(map_file)

        return render_template('index.html', 
                               result = formatted_dirs, 
                               total_duration = formatted_duration,
                               itinerary = itinerary,
                               )

    return render_template('input.html')


@app.route('/show_directions', methods=['GET'])
def show_directions():

    formatted_dirs = session.get('formatted_dirs')
    if formatted_dirs is None:
        return redirect(url_for('index'))

    return render_template('directions.html', formatted_dirs=formatted_dirs)



if __name__ == '__main__':
    app.run(debug=True)



