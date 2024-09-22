import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Set up a title for the app
st.title("Map-Based Piping Layout Tool with Accurate Pipe Length Calculation")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle (region selection).
2. Place points (representing facilities) within the selected region.
3. Draw lines (pipes) and calculate real-world distances.
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

# Function to add a point (site) with customizable color and name
def add_point(lat, lng, name, color):
    folium.Marker(location=[lat, lng], popup=name, icon=folium.Icon(color=color)).add_to(m)

# Function to draw a line (pipe) with customizable color and name
def draw_line(coords, name, color):
    folium.PolyLine(locations=coords, color=color, tooltip=name, weight=3).add_to(m)

# Store total pipe length
total_pipe_length = 0

# List to store points (sites)
points = []

# Render the map and handle the drawings (rectangles and lines)
output = st_folium(m, width=725, height=500)

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

            # Add a point (site) inside the selected area (use center point)
            mid_lat = (sw_corner[1] + ne_corner[1]) / 2
            mid_lng = (sw_corner[0] + ne_corner[0]) / 2
            add_point(mid_lat, mid_lng, point_name, point_color)
            points.append((mid_lat, mid_lng, point_name, point_color))

        elif shape['geometry']['type'] == 'LineString':  # Line drawn (pipe)
            coords = shape['geometry']['coordinates']
            pipe_length = 0
            # Calculate the total distance of the pipe (sum of segment distances)
            for i in range(len(coords) - 1):
                start = (coords[i][1], coords[i][0])  # Lat, Lng
                end = (coords[i+1][1], coords[i+1][0])  # Lat, Lng
                segment_length = calculate_distance(start, end)
                pipe_length += segment_length
            
            total_pipe_length += pipe_length
            draw_line(coords, line_name, line_color)
            st.sidebar.success(f"Pipe Length: {pipe_length:.2f} meters")

# Display the total pipe length in the sidebar
st.sidebar.subheader("Total Pipe Length")
st.sidebar.write(f"{total_pipe_length:.2f} meters")

# Display all points (sites) in the sidebar
st.sidebar.subheader("Placed Points (Sites)")
for i, point in enumerate(points, start=1):
    st.sidebar.write(f"{i}. {point[2]} (Color: {point[3]}, Location: {point[0]:.5f}, {point[1]:.5f})")
