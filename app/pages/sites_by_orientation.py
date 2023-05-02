import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_folium import folium_static
import folium

from math import radians, sin, cos, sqrt, atan2

# define the coordinates of Paris
paris_lat, paris_lon = radians(48.8566), radians(2.3522)

def compute_distance(lat, lon):
    R = 6371.0  # radius of the earth in km
    lat1, lon1 = radians(lat), radians(lon)
    lat2, lon2 = paris_lat, paris_lon
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return round(distance)

# Load data
df = px.data.wind()
sites = pd.read_csv(r'data/ffvl_site.csv')
sites = sites[(sites['site_type']=='vol') & (sites['site_sous_type']=='Décollage')& (sites['site_sous_type']=='Décollage')].sort_values(by='nom',ascending=True)
sites['distance_from_Paris']=sites.apply(lambda row: compute_distance(row['lat'], row['lon']), axis=1)
max_distance = st.sidebar.slider('Maximum distance from Paris as a crow flies(km)', min_value=0, max_value=1000, value=100)

sites = sites[sites['distance_from_Paris'] <= max_distance]

# define the compass directions in the correct order
compass_order = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
des_orient = st.sidebar.multiselect('Sites to be displayed by orientation', options=compass_order, default=compass_order)

sites = sites[sites['orientation'].isin(des_orient)]

# split the tags column into a list and duplicate the rows
sites = sites.assign(orientation=lambda x: x['orientation'].str.split(',')).explode('orientation')

# modify the 'orientation' column to a categorical variable with the correct order
sites['orientation'] = pd.Categorical(sites['orientation'], categories=compass_order, ordered=True)

# sort the DataFrame by the 'orientation' column
sites = sites.sort_values(by='orientation')

# reset the index
sites = sites.reset_index(drop=True)

# Create Streamlit app
st.title('Site Orientation Data Visualization')

# Create Plotly Express figure
fig = px.scatter_polar(sites, r="distance_from_Paris", theta="orientation", color="nom",hover_data=['nom']+['sous_nom'])
st.plotly_chart(fig)



# Add Streamlit table
st.title('Site Data')
site_data = sites[['nom', 'sous_nom', 'cp', 'ville', 'alt',
       'acces', 'trajet_parcking', 'trajet_attero_deco', 'handi'
       , 'vent_favo', 'vent_defavo', 'conditions_ideales',
       'balise', 'webcam', 'signaletique', 'description', 'restrictions',
       'reg_aerienne', 'dangers', 'date_modification','distance_from_Paris']]
sites_data = site_data.drop_duplicates(subset=['nom', 'sous_nom', 'cp', 'ville', 'alt',
       'acces', 'trajet_parcking', 'trajet_attero_deco', 'handi'
       , 'vent_favo', 'vent_defavo', 'conditions_ideales',
       'balise', 'webcam', 'signaletique', 'description', 'restrictions',
       'reg_aerienne', 'dangers', 'date_modification','distance_from_Paris'])
st.dataframe(sites_data)


# Add Streamlit map
st.title('Site Locations')
#st.map(sites[['lat', 'lon']])

m = folium.Map(location=[46.1853369, 5.570780999999999], zoom_start=4)

for index, row in sites.iterrows():
    html = """{}<br>
    <sub><b></b> <br>
    {}</sub><br>
    <sub><b>Vents favorables</b> <br>
    {}</sub>
    """.format(row['nom'],str(row['sous_nom']),str(row['vent_favo']))


    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=html
    ).add_to(m)

# call to render Folium map in Streamlit
folium_static(m)
