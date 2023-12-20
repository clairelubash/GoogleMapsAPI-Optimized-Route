# Optimizing Routes with Google Maps API
A Flask application that leverages the suite of Google Maps APIs to provide the optimal driving route given an origin, and any points of interest.

- The Places API simplifies user input by allowing the use of 'keywords' instead of specific addresses, enhancing the user experience.
- After specifying the starting location and desired points of interest, the application's UI presents the optimal itinerary, along with its corresponding driving time. An interactive Folium map illustrates the route, and step-by-step directions are provided by the Directions API.
> **_Example:_** Imagine a user leaving their apartment to run errands at Target and ShopRite. Through the application's interface, the user can input their apartment building, Target, and ShopRite, prompting the application to find the store locations which would generate a route that minimizes driving time. 

## Installation
1. Clone the repository:
```shell
git clone https://github.com/clairelubash/GoogleMapsAPI-Optimized-Route.git
cd GoogleMapsAPI-Optimized-Route
```
2. Create a virtual environment:
```shell
python3 -m venv venv
```
3. Activate the virtual environment:
```shell
source venv/bin/activate
```
4. Install dependencies:
```shell
pip install -r requirements.txt
```
5. Set up Google Maps API:
- Obtain an API key from the [Google Cloud Platform Console](console.cloud.google.com).
- Enable the Directions API, Places API, and Geocoding API.
- Create a .env file and add your API key.
6. Run the Flask app:
```shell
python3 main.py
```
7. Access the applictaion in your browser at `http://localhost:5000`. 

## Usage
- Open web application in browser.
- Enter your starting location and keywords representing the types of places you want to visit (e.g., Target, ShopRite) in a comma-separated list. 
- Click on the "Get Optimized Route" button to calculate the optimized route. 
- The UI will display the ideal itineary, total driving duration, and an interactive map with the route outlined. For more detailed directions, click on the "Step-By-Step Directions" button. 

### Helpful Links
- [Google Maps Platform API Documentation](https://developers.google.com/maps/documentation)
- [Python Client for Google Maps Services](https://github.com/googlemaps/google-maps-services-python)
