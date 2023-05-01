import streamlit as st
import pandas as pd
import requests
import openweathermapy as owm
import datetime

# Set up API keys
OPENWEATHERMAP_API_KEY = '93d10193a47c250d1fc0c68b79fa0046'
GOOGLE_MAPS_API_KEY = 'AIzaSyCr6_eqW32A52hYTIlJ0cptG8avoK6pkLg'

def get_weather_emoji(description: str) -> str:
    """
    Returns the corresponding emoji based on a given weather description.
    """
    # Create a dictionary mapping weather conditions to emojis
    emojis = {
        'Thunderstorm': '⛈️',
        'Drizzle': '🌧️',
        'Rain': '🌧️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Smoke': '🌫️',
        'Haze': '🌫️',
        'Dust': '🌫️',
        'Fog': '🌫️',
        'Sand': '🌫️',
        'Ash': '🌫️',
        'Squall': '🌪️',
        'Tornado': '🌪️',
        'Clear': '☀',
        'Clouds': '☁️',
        'Few clouds': '⛅',
        'Scattered clouds': '🌥️',
        'Broken clouds': '☁️',
        'Overcast clouds': '☁️',
    }
    
    # Get the emoji for the given weather condition
    return emojis.get(description, '')

def get_wind_direction_emoji(degrees):
    """
    Returns the corresponding wind direction emoji based on wind direction in degrees.
    """
    # Define wind direction sectors
    directions = {
        'N': [*range(-0, 23), *range(338, 361)],
        'NE': range(23, 68),
        'E': range(68, 113),
        'SE': range(113, 158),
        'S': range(158, 203),
        'SW': range(203, 248),
        'W': range(248, 293),
        'NW': range(293, 338)
    }
    
    # Find the corresponding wind direction sector
    for direction, sector in directions.items():
        if degrees in sector:
            return f"{direction}"
    
    # If wind direction is not found, return a generic wind emoji
    return ":wind_face:"
    

# Load the FFVL sites dataset
sites = pd.read_csv('ffvl_site.csv')
sites = sites[(sites['site_type']=='vol') & (sites['site_sous_type']=='Décollage')& (sites['site_sous_type']=='Décollage')].sort_values(by='nom',ascending=True)

# Rename columns for consistency
sites = sites.rename(columns={'site': 'nom', 'latitude': 'lat', 'longitude': 'lon'})

# Select the sites to display
selected_sites = st.multiselect('Select sites to display', sites['nom'])

# Set up the starting point input widget
start_point = st.text_input('Starting point (address or name)', 'Paris')

# Get the weather and wind forecast for each site
for site_index, site_row in sites.iterrows():
    if site_row['nom'] not in selected_sites:
        continue  # Skip sites that were not selected
        
    # Get the site location
    site_lat = site_row['lat']
    site_lon = site_row['lon']
    
    # Calculate the distance and duration from the starting point using the Google Maps Distance Matrix API
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={start_point}&destinations={site_lat},{site_lon}&mode=driving&key={GOOGLE_MAPS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    distance = data['rows'][0]['elements'][0]['distance']['text']
    duration = data['rows'][0]['elements'][0]['duration']['text']
    
    # Calculate the price from the starting point
    price = round(float(distance.split()[0]) * 0.5, 2) # Assuming 0.5 € per km
    
    # Get the weather and wind forecast for the next 5 days using the OpenWeatherMap API
    forecast = owm.get_forecast_hourly(lat=site_lat, lon=site_lon, APPID=OPENWEATHERMAP_API_KEY)
    forecast_data = []
    for weather in forecast:
        forecast_item = {
            'date': datetime.datetime.fromtimestamp(weather['dt']).strftime('%Y-%m-%d %H:%M:%S'),
            'temp': round((float(weather['main']['temp'])-272.15), 1),
            'pressure': weather['main']['pressure'],
            'description': weather['weather'][0]['description'],
            'icon': weather['weather'][0]['icon'],
            'clouds': weather['clouds']['all'],
            'wind_speed': round(weather['wind']['speed'] * 3.6), # Convert from m/s to km/h
            'wind_deg': weather['wind']['deg'],
            'gust': round(weather['wind']['gust'] * 3.6) # Convert from m/s to km/h
        }
        forecast_data.append(forecast_item)
    
    # Create a table to display the information
    table_data = [
        ['Date', 'Temperature (°C)', 'Pressure', 'Weather Description', 'Weather Icon', 'Clouds', 'Wind Speed (km/h)', 'Wind Direction', 'Wind Gust (km/h)']
    ]
    
    # Add the weather and wind forecast to the table
    for forecast_item in forecast_data:
        icon_url = f"http://openweathermap.org/img/w/{forecast_item['icon']}.png"
        icon = requests.get(icon_url).content
        table_data.append([
            forecast_item['date'],
            f"{forecast_item['temp']} °C",
            f"{forecast_item['pressure']} hPa",
            forecast_item['description'],
            'icon !!',
            f"{forecast_item['clouds']}%",
            f"{forecast_item['wind_speed']} km/h",
            get_wind_direction_emoji(forecast_item['wind_deg']),
            f"{forecast_item['gust']} km/h"
        ])

    table_data = pd.DataFrame(table_data)
    # Display the information
    st.write(f"Site: {site_row['nom']}")
    st.write('Distance from starting point : '+ distance)
    st.write('Duration from starting point : '+ duration)
    st.write('Price from starting point : '+ f"{price} €")
    st.table(table_data)
    st.write('---')

