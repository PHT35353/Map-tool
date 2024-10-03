import streamlit as st
import pydeck as pdk
from streamlit_drawable_canvas import st_canvas
from mapbox import Geocoder
import math

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

# Initialize mapbox-gl-draw features (Lines, Points, Areas)
draw_mode = st.sidebar.selectbox(
    "Drawing Tool",
    ("None", "Line", "Area", "Point")
)

# Color picker for drawing shapes
color = st.sidebar.color_picker("Pick a color for the drawing")

# Get the location coordinates from search
response = geocoder.forward(location).geojson()
coordinates = response['features'][0]['geometry']['coordinates']

# Create a Pydeck map with 3D buildings
st.pydeck_chart(
    pdk.Deck(
        map_style=map_styles[map_style],
        initial_view_state=pdk.ViewState(
            latitude=coordinates[1],
            longitude=coordinates[0],
            zoom=zoom_level,
            pitch=60,  # Tilt to show 3D buildings
            bearing=0
        ),
        layers=[
            pdk.Layer(
                "GeoJsonLayer",
                data="https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-building/3d-buildings.json",  # Example 3D building data
                extruded=True,
                wireframe=True,
                get_fill_color=[255, 255, 255],
                get_line_color=[0, 0, 0],
                get_elevation="height",
            )
        ],
        mapbox_key=mapbox_token
    )
)

# Create a drawable canvas for drawing pipes or marking locations
canvas = st_canvas(
    stroke_width=3,
    stroke_color=color,
    background_color="#eee",
    height=400,
    width=800,
    drawing_mode=draw_mode,
    key="canvas",
)

# Function to calculate distance between two points (Haversine formula)
def calculate_distance(coord1, coord2):
    R = 6371000  # Radius of Earth in meters
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in meters

# Show the drawn lines and calculate distances
if canvas.image_data is not None:
    st.write("Line drawn on map!")

    # Calculate the distance of the drawn lines (if any)
    if draw_mode == "Line" and len(canvas.data['objects']) > 1:
        point1 = canvas.data['objects'][0]['coordinates']
        point2 = canvas.data['objects'][1]['coordinates']
        distance = calculate_distance(point1, point2)
        st.write(f"Distance between points: {distance} meters")

# Allow user to mark areas and calculate dimensions
if draw_mode == "Area":
    st.write("You can mark an area and measure its dimensions.")
    # Custom logic to measure the area can be added here

# Allow user to save or name landmarks
if draw_mode == "Point":
    landmark_name = st.text_input("Name this landmark")
    st.write(f"Landmark saved as: {landmark_name}")

# Option to rotate map view
rotate_angle = st.sidebar.slider("Rotate Map", -180, 180, 0)

# Update the Pydeck map with rotation
st.pydeck_chart(
    pdk.Deck(
        map_style=map_styles[map_style],
        initial_view_state=pdk.ViewState(
            latitude=coordinates[1],
            longitude=coordinates[0],
            zoom=zoom_level,
            pitch=60,
            bearing=rotate_angle
        ),
        layers=[
            pdk.Layer(
                "GeoJsonLayer",
                data="https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-building/3d-buildings.json",  # Example 3D building data
                extruded=True,
                wireframe=True,
                get_fill_color=[255, 255, 255],
                get_line_color=[0, 0, 0],
                get_elevation="height",
            )
        ],
        mapbox_key=mapbox_token
    )
)
