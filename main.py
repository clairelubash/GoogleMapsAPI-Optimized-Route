from dotenv import load_dotenv
from utils import *
from flask import Flask, request, render_template


load_dotenv()


app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':

        param1 = str(request.form['param1'])
        param2 = [x.strip() for x in request.form['param2'].split(',')]
        
        result, dirs, total_duration = get_optimized_route(param1, param2)

        formatted_dirs = format_instructions(dirs)
        formatted_duration = str(total_duration) + ' minutes'

        generated_map = generate_map(result)

        map_file = "templates/map.html"
        generated_map.save(map_file)

        return render_template('index.html', 
                               result = formatted_dirs, 
                               total_duration = formatted_duration
                               )

    return render_template('input.html')



if __name__ == '__main__':
    app.run(debug=True)



