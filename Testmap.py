import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from folium import plugins

# Set up a title for the app
st.title("Interactive Map Tool with Customizable Circle Markers and Red Lines")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle.
2. Place Circle Markers (with custom names and colors) within the selected area.
3. Draw lines (pipes) between Circle Markers, where all lines are red.
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
        'polyline': {'shapeOptions': {'color': 'red', 'weight': 3}},  # All lines (pipes) will be red
        'polygon': False,
        'circle': False,
        'rectangle': {'shapeOptions': {'color': 'green', 'weight': 2}},  # Allow drawing a rectangle (area selection)
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
total_pipe_length = 0

# Function to update the marker with the custom name and color
def create_marker(lat, lng, name="Marker", color="blue"):
    return folium.CircleMarker(
        location=[lat, lng],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=name
    )

# HTML form for the popup to input names and colors for Circle Markers
def marker_popup_form(lat, lng, marker_id):
    return f"""
    <form id="marker_form_{marker_id}">
        <label for="name">Point Name:</label><br>
        <input type="text" id="name" value="New Point"><br>
        <label for="color">Point Color:</label><br>
        <input type="color" id="color" value="#ff0000"><br>
        <input type="button" value="Submit" onclick="updateMarker({marker_id}, {lat}, {lng})">
    </form>
    <script>
    function updateMarker(id, lat, lng) {{
        var name = document.getElementById('marker_form_' + id).elements['name'].value;
        var color = document.getElementById('marker_form_' + id).elements['color'].value;
        window.parent.postMessage({{'id': id, 'name': name, 'color': color, 'lat': lat, 'lng': lng}}, '*');
    }}
    </script>
    """

# Render the map and handle the drawings
output = st_folium(m, width=725, height=500)

# Check if any drawings were made
if output and output['all_drawings']:
    for shape in output['all_drawings']:
        if shape['geometry']['type'] == 'Polygon':  # Rectangle drawn (region selection)
            coords = shape['geometry']['coordinates'][0]
            sw_corner = coords[0]  # Southwest corner
            ne_corner = coords[2]  # Northeast corner

            # Calculate real-world dimensions of the selected rectangle
            width = calculate_distance((sw_corner[1], sw_corner[0]), (ne_corner[1], sw_corner[0]))
            height = calculate_distance((sw_corner[1], sw_corner[0]), (sw_corner[1], ne_corner[0]))

            st.sidebar.success(f"Selected Region Dimensions: Width = {width:.2f} meters, Height = {height:.2f} meters")
            st.sidebar.info("Now, you can place points within the selected area.")

        elif shape['geometry']['type'] == 'Point':  # Point (circle marker) placed
            lat = shape['geometry']['coordinates'][1]
            lng = shape['geometry']['coordinates'][0]
            
            # Unique marker ID for identifying the specific marker
            marker_id = len(points) + 1

            # Add the initial Circle Marker with the popup to customize name and color
            folium.CircleMarker(
                location=[lat, lng],
                radius=8,
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(marker_popup_form(lat, lng, marker_id), max_width=300)
            ).add_to(m)
            points.append((lat, lng))

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

            # Draw the line with a fixed red color
            folium.PolyLine(
                locations=[(coord[1], coord[0]) for coord in coords],
                color="red",  # All lines (pipes) are red
                weight=3,
            ).add_to(m)
            lines.append(coords)

# Display the total pipe length in the sidebar
st.sidebar.subheader("Total Pipe Length")
st.sidebar.write(f"{total_pipe_length:.2f} meters")
