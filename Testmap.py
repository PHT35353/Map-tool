import streamlit as st
import pydeck as pdk
from mapbox import Geocoder

# Configure the Streamlit page layout
st.set_page_config(page_title="Piping Map Tool", layout="wide")

# Set your Mapbox access token here
mapbox_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# Initialize Geocoder from Mapbox
geocoder = Geocoder(access_token=mapbox_token)

# Sidebar for user options
st.sidebar.header("Piping Map Tool")
st.sidebar.markdown("Select options below:")

# Option for satellite or street view
map_style = st.sidebar.radio("Choose Map Style", ("Satellite", "Street View"))
map_styles = {
    "Satellite": "mapbox://styles/mapbox/satellite-v9",
    "Street View": "mapbox://styles/mapbox/streets-v11"
}

# Allow user to search for a location
location = st.sidebar.text_input("Search for a location", "New York, USA")

# Zoom level for the map
zoom_level = st.sidebar.slider("Select zoom level", 1, 20, 15)

# Get the location coordinates from search
response = geocoder.forward(location).geojson()
coordinates = response['features'][0]['geometry']['coordinates']

# Simplified Pydeck map without 3D buildings
st.pydeck_chart(
    pdk.Deck(
        map_style=map_styles[map_style],
        initial_view_state=pdk.ViewState(
            latitude=coordinates[1],
            longitude=coordinates[0],
            zoom=zoom_level,
            pitch=45,  # Add pitch for a slight 3D effect
            bearing=0
        ),
        mapbox_key=mapbox_token
    )
)
