import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Set up a title for the app
st.title("Interactive Map Tool with Points and Customizable Lines")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle (region selection).
2. Place points interactively by clicking on the map within the selected area.
3. Draw lines (pipes) between the points and calculate real-world distances.
4. Customize the colors and names of both points and lines.
5. Search for a location by entering latitude and longitude.
""")

# Set the starting location and zoom to the Netherlands
default_location = [52.3676, 4.9041]  # Amsterdam, Netherlands
zoom_start = 13

# Sidebar to manage the map interactions
st.sidebar.title("Map Interactions")

# Search for a location by Latitude and Longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

# Create a Folium map with Mapbox Satellite layer (one map)
m = folium.Map(location=default_location, zoom_start=zoom_start)

# Add Mapbox Satellite layer (replace this with your valid token)
tile_url = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"
folium.TileLayer(tiles=tile_url, attr='Mapbox').add_to(m)

# Add drawing tool for selecting a region and drawing lines
draw = folium.plugins.Draw(
    export=True,  # Allow exporting shapes as GeoJSON
    draw_options={'polyline': True, 'polygon': False, 'circle': False, 'rectangle': True, 'marker': False}
)
draw.add_to(m)

# Function to calculate the geodesic distance between two points
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).meters

# Store total pipe length
total_pipe_length = 0

# List to store points (sites) and lines (pipes)
points = []
lines = []

# Color options for lines and points
color_options = ["red", "blue", "green", "purple", "orange", "darkred", "lightred", "darkblue", "darkgreen"]

# Sidebar options for customizing points (sites)
st.sidebar.subheader("Point (Site) Options")
point_name = st.sidebar.text_input("Enter Point Name")
point_color = st.sidebar.selectbox("Select Point Color", color_options)

# Sidebar options for customizing lines (pipes)
st.sidebar.subheader("Line (Pipe) Options")
line_name = st.sidebar.text_input("Enter Line Name")
line_color = st.sidebar.selectbox("Select Line Color", color_options)

# Function to add a point with customizable color and name
def add_point(lat, lng, name, color):
    folium.Marker(location=[lat, lng], popup=name, icon=folium.Icon(color=color)).add_to(m)

# Function to draw a line with customizable color and name
def draw_line(coords, name, color):
    folium.PolyLine(locations=coords, color=color, tooltip=name, weight=3).add_to(m)

# Render the map and handle the drawings (rectangles and lines)
output = st_folium(m, width=725, height=500)

# Check if any drawings were made (rectangles or lines)
if output and output['all_drawings']:
    for shape in output['all_drawings']:
        if shape['geometry']['type'] == 'Polygon':  # Rectangle drawn (region selection)
            coords = shape['geometry']['coordinates'][0]
            sw_corner = coords[0]  # Southwest corner
            ne_corner = coords[2]  # Northeast corner

            # Calculate real-world dimensions of the selected rectangle
            width = calculate_distance((sw_corner[1], sw_corner[0]), (ne_corner[1], sw_corner[0]))
            height = calculate_distance((sw_corner[1], sw_corner[0]), (sw_corner[1], ne_corner[0]))

            st.sidebar.success(f"Region Dimensions: Width: {width:.2f} meters, Height: {height:.2f} meters")
            st.sidebar.info("Click on the map to place points within the selected area.")

# Handle point placement by clicking on the map
if output and output['last_clicked']:
    click_location = output['last_clicked']
    lat, lng = click_location['lat'], click_location['lng']
    points.append((lat, lng, point_name, point_color))
    add_point(lat, lng, point_name, point_color)
    st.success(f"Placed point at ({lat:.5f}, {lng:.5f}) with name '{point_name}' and color '{point_color}'.")

# Allow user to connect points with lines (pipes) and calculate distance
if len(points) > 1:
    start_index = st.sidebar.selectbox("Select Starting Point", range(1, len(points) + 1))
    end_index = st.sidebar.selectbox("Select Ending Point", range(1, len(points) + 1))
    if st.sidebar.button("Connect Points"):
        start_point = points[start_index - 1]
        end_point = points[end_index - 1]
        line_coords = [(start_point[0], start_point[1]), (end_point[0], end_point[1])]
        draw_line(line_coords, line_name, line_color)
        line_distance = calculate_distance((start_point[0], start_point[1]), (end_point[0], end_point[1]))
        total_pipe_length += line_distance
        st.sidebar.write(f"Distance between '{start_point[2]}' and '{end_point[2]}': {line_distance:.2f} meters")

# Display total pipe length in the sidebar
st.sidebar.subheader("Total Pipe Length")
st.sidebar.write(f"{total_pipe_length:.2f} meters")

# Display all placed points in the sidebar
st.sidebar.subheader("Placed Points")
for i, point in enumerate(points, start=1):
    st.sidebar.write(f"{i}. {point[2]} (Color: {point[3]}, Location: {point[0]:.5f}, {point[1]:.5f})")
