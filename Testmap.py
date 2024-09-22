import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from folium import plugins

# Set up a title for the app
st.title("Interactive Map Tool with Customizable Rectangles (Squares)")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle.
2. Change the name and color of the selected rectangle (square).
3. View the real-world dimensions of the selected area.
""")

# Set the starting location and zoom to the Netherlands
default_location = [52.3676, 4.9041]  # Amsterdam, Netherlands
zoom_start = 13

# Sidebar to manage the map interactions
st.sidebar.title("Map Controls")

# Search for a location by Latitude and Longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

# Initialize session state variables
if "rectangles" not in st.session_state:
    st.session_state["rectangles"] = []
    st.session_state["rectangle_names"] = []
    st.session_state["rectangle_colors"] = []

# Create the map (only once)
m = folium.Map(location=default_location, zoom_start=zoom_start)

# Add Mapbox Satellite layer (replace this with your valid token)
tile_url = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"
folium.TileLayer(tiles=tile_url, attr='Mapbox').add_to(m)

# Add drawing tool for selecting a region (rectangle) and modifying it
draw = plugins.Draw(
    export=True,  # Allow exporting shapes as GeoJSON
    draw_options={
        'polyline': False,
        'polygon': False,
        'circle': False,
        'rectangle': {'shapeOptions': {'color': 'green', 'weight': 2}},  # Allow drawing a rectangle
        'circlemarker': False,
    },
    edit_options={'edit': False}  # Disable edit functionality for simplicity
)
draw.add_to(m)

# Function to calculate the geodesic distance between two points
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).meters

# Process any new drawings on the map
output = st_folium(m, width=725, height=500)

# Handle new drawings (rectangles)
if output and output['all_drawings']:
    for shape in output['all_drawings']:
        if shape['geometry']['type'] == 'Polygon':  # Rectangle drawn
            coords = shape['geometry']['coordinates'][0]
            sw_corner = coords[0]  # Southwest corner
            ne_corner = coords[2]  # Northeast corner

            # Store rectangle in session state
            st.session_state["rectangles"].append(coords)
            st.session_state["rectangle_names"].append(f"Rectangle {len(st.session_state['rectangles'])}")
            st.session_state["rectangle_colors"].append("#00ff00")  # Default color is green

            # Calculate real-world dimensions of the selected rectangle
            width = calculate_distance((sw_corner[1], sw_corner[0]), (ne_corner[1], sw_corner[0]))
            height = calculate_distance((sw_corner[1], sw_corner[0]), (sw_corner[1], ne_corner[0]))

            st.sidebar.success(f"Selected Rectangle Dimensions: Width = {width:.2f} meters, Height = {height:.2f} meters")

# Sidebar for modifying rectangles (name and color)
if len(st.session_state["rectangles"]) > 0:
    st.sidebar.subheader("Modify Rectangles")
    rectangle_idx = st.sidebar.selectbox("Select Rectangle", range(1, len(st.session_state["rectangles"]) + 1))
    new_name = st.sidebar.text_input("Rectangle Name", value=st.session_state["rectangle_names"][rectangle_idx - 1])
    new_color = st.sidebar.color_picker("Rectangle Color", value=st.session_state["rectangle_colors"][rectangle_idx - 1])

    # Update the selected rectangle's name and color
    st.session_state["rectangle_names"][rectangle_idx - 1] = new_name
    st.session_state["rectangle_colors"][rectangle_idx - 1] = new_color

# Recreate the map with updated rectangles
for i, coords in enumerate(st.session_state["rectangles"]):
    folium.Polygon(
        locations=[(lat, lng) for lng, lat in coords],  # Convert (lng, lat) to (lat, lng)
        color=st.session_state["rectangle_colors"][i],
        fill=True,
        fill_color=st.session_state["rectangle_colors"][i],
        fill_opacity=0.3,
        popup=st.session_state["rectangle_names"][i]
    ).add_to(m)

# Render the updated map (only once)
st_folium(m, width=725, height=500)
