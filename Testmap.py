import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from folium import plugins

# Set up a title for the app
st.title("Interactive Map Tool with Customizable Shapes and Lines")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle and customizing its name and color.
2. Place Circle Markers (with custom names and colors) within the selected area.
3. Draw lines (pipes) between Circle Markers with customizable names and colors. Each line will display its length.
4. Search for a location by entering latitude and longitude (in the sidebar).
""")

# Set the starting location and zoom to the Netherlands
default_location = [52.3676, 4.9041]  # Amsterdam, Netherlands
zoom_start = 13

# Sidebar to manage the map interactions
st.sidebar.title("Search by Coordinates")

# Search for a location by Latitude and Longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

# Create a Folium map with Mapbox Satellite layer (for interactive map controls)
m = folium.Map(location=default_location, zoom_start=zoom_start)

# Add Mapbox Satellite layer (replace this with your valid token)
tile_url = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"
folium.TileLayer(tiles=tile_url, attr='Mapbox').add_to(m)

# Add drawing tool for selecting a region, placing circle markers, and drawing lines
draw = plugins.Draw(
    export=True,  # Allow exporting shapes as GeoJSON
    draw_options={
        'polyline': {'shapeOptions': {'color': 'red', 'weight': 3}},  # Default color for lines (pipes)
        'polygon': False,
        'circle': False,
        'rectangle': {'shapeOptions': {'color': 'green', 'weight': 2}},  # Default color for rectangles
        'circlemarker': {'repeatMode': True},  # Enable Circle Marker for point placement
    },
    edit_options={'edit': False}  # Disable edit functionality for simplicity
)
draw.add_to(m)

# Function to calculate the geodesic distance between two points
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).meters

# Store points, lines, and pipe lengths
points = []
lines = []
rectangles = []
total_pipe_length = 0

# Render the map and handle the drawings
output = st_folium(m, width=725, height=500)  # Removed extra rendering

# Check if any drawings were made
if output and output['all_drawings']:
    for idx, shape in enumerate(output['all_drawings']):
        if shape['geometry']['type'] == 'Polygon':  # Rectangle drawn (region selection)
            coords = shape['geometry']['coordinates'][0]
            sw_corner = coords[0]  # Southwest corner
            ne_corner = coords[2]  # Northeast corner

            # Sidebar customization for this specific rectangle
            st.sidebar.subheader(f"Customize Rectangle {idx + 1}")
            rectangle_name = st.sidebar.text_input(f"Enter name for Rectangle {idx + 1}", f"Rectangle {idx + 1}")
            rectangle_color = st.sidebar.color_picker(f"Choose color for Rectangle {idx + 1}", "#00ff00")

            # Calculate the real-world dimensions of the selected rectangle
            width = calculate_distance((sw_corner[1], sw_corner[0]), (ne_corner[1], sw_corner[0]))
            height = calculate_distance((sw_corner[1], sw_corner[0]), (sw_corner[1], ne_corner[0]))

            # Add rectangle with custom name and color
            folium.Rectangle(
                bounds=[(sw_corner[1], sw_corner[0]), (ne_corner[1], ne_corner[0])],
                color=rectangle_color,
                fill=True,
                fill_opacity=0.5,
                popup=rectangle_name
            ).add_to(m)
            st.sidebar.success(f"Rectangle {rectangle_name} drawn: Width = {width:.2f} meters, Height = {height:.2f} meters")

        elif shape['geometry']['type'] == 'Point':  # Point (circle marker) placed
            lat = shape['geometry']['coordinates'][1]
            lng = shape['geometry']['coordinates'][0]
            
            # Sidebar customization for this specific marker
            st.sidebar.subheader(f"Customize Marker {idx + 1}")
            marker_name = st.sidebar.text_input(f"Enter name for Marker {idx + 1}", f"Marker {idx + 1}")
            marker_color = st.sidebar.color_picker(f"Choose color for Marker {idx + 1}", "#0000ff")

            # Add the Circle Marker with the popup to customize name and color
            folium.CircleMarker(
                location=[lat, lng],
                radius=8,
                fill=True,
                fill_opacity=0.7,
                color=marker_color,
                fill_color=marker_color,
                popup=marker_name
            ).add_to(m)
            points.append((lat, lng))

        elif shape['geometry']['type'] == 'LineString':  # Line drawn (pipe)
            coords = shape['geometry']['coordinates']
            pipe_length = 0

            # Sidebar customization for this specific line
            st.sidebar.subheader(f"Customize Line {idx + 1}")
            line_name = st.sidebar.text_input(f"Enter name for Line {idx + 1}", f"Line {idx + 1}")
            line_color = st.sidebar.color_picker(f"Choose color for Line {idx + 1}", "#ff0000")

            # Calculate the total distance of the pipe (sum of segment distances)
            for i in range(len(coords) - 1):
                start = (coords[i][1], coords[i][0])  # Lat, Lng
                end = (coords[i+1][1], coords[i+1][0])  # Lat, Lng
                segment_length = calculate_distance(start, end)
                pipe_length += segment_length

            total_pipe_length += pipe_length

            # Draw the line with custom color and show distance
            folium.PolyLine(
                locations=[(coord[1], coord[0]) for coord in coords],
                color=line_color,  # Custom color selected
                weight=3,
                popup=f"{line_name}: {pipe_length:.2f} meters"
            ).add_to(m)
            lines.append(coords)

# Display the total pipe length in the sidebar
st.sidebar.subheader("Total Pipe Length")
st.sidebar.write(f"{total_pipe_length:.2f} meters")

# **Make sure to render the map only once here, with all the shapes added**
st_folium(m, width=725, height=500)
