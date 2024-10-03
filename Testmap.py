import streamlit as st
import pydeck as pdk
from mapbox import Geocoder

# Configure the Streamlit page layout
st.set_page_config(page_title="Piping Map Tool", layout="wide")

# Set your Mapbox access token here
mapbox_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# Set the Mapbox token via Streamlit
st.session_state["mapbox_api_key"] = mapbox_token

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

try:
    # Get the location coordinates from search
    response = geocoder.forward(location).geojson()
    coordinates = response['features'][0]['geometry']['coordinates']
    st.write(f"Coordinates for {location}: {coordinates}")
except Exception as e:
    st.error(f"Error fetching coordinates: {e}")
    coordinates = [-74.0060, 40.7128]  # Fallback to default coordinates (New York City)

# Simplified Pydeck map without 3D buildings
try:
    st.pydeck_chart(
        pdk.Deck(
            map_style=map_styles[map_style],
            initial_view_state=pdk.ViewState(
                latitude=coordinates[1],  # Latitude
                longitude=coordinates[0],  # Longitude
                zoom=zoom_level,
                pitch=45,  # Add pitch for a slight 3D effect
                bearing=0
            )
        )
    )
except Exception as e:
    st.error(f"Error rendering the map: {e}")
