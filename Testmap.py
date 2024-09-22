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
st.sidebar.title("Map Controls")

# Search for a location by Latitude and Longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

# Store points and lines
if "points" not in st.session_state:
    st.session_state.points = []
    st.session_state.point_names = []
    st.session_state.point_colors = []
    st.session_state.lines = []
    st.session_state.total_pipe_length = 0

# Create the map
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

# Handle the drawings (region selection, placing points, drawing lines)
output = st_folium(m, width=725, height=500)

# Process any new drawings on the map
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

        elif shape['geometry']['type'] == 'Point':  # Circle Marker placed
            lat = shape['geometry']['coordinates'][1]
            lng = shape['geometry']['coordinates'][0]
            st.session_state.points.append((lat, lng))  # Save marker coordinates
            st.session_state.point_names.append(f"Marker {len(st.session_state.points)}")  # Assign a default name
            st.session_state.point_colors.append("#3388ff")  # Default blue color

        elif shape['geometry']['type'] == 'LineString':  # Line drawn (pipe)
            coords = shape['geometry']['coordinates']
            pipe_length = 0

            # Calculate the total distance of the pipe (sum of segment distances)
            for i in range(len(coords) - 1):
                start = (coords[i][1], coords[i][0])  # Lat, Lng
                end = (coords[i+1][1], coords[i+1][0])  # Lat, Lng
                segment_length = calculate_distance(start, end)
                pipe_length += segment_length

            st.session_state.total_pipe_length += pipe_length
            st.session_state.lines.append(coords)

# Sidebar for modifying Circle Markers (name and color)
if len(st.session_state.points) > 0:
    st.sidebar.subheader("Modify Markers")
    marker_idx = st.sidebar.selectbox("Select Marker", range(1, len(st.session_state.points) + 1))
    new_name = st.sidebar.text_input("Marker Name", value=st.session_state.point_names[marker_idx - 1])
    new_color = st.sidebar.color_picker("Marker Color", value=st.session_state.point_colors[marker_idx - 1])

    # Update the selected marker's name and color
    st.session_state.point_names[marker_idx - 1] = new_name
    st.session_state.point_colors[marker_idx - 1] = new_color

# Recreate the map with updated markers
for i, (lat, lng) in enumerate(st.session_state.points):
    folium.CircleMarker(
        location=[lat, lng],
        radius=8,
        color=st.session_state.point_colors[i],
        fill=True,
        fill_color=st.session_state.point_colors[i],
        fill_opacity=0.7,
        popup=st.session_state.point_names[i]
    ).add_to(m)

# Recreate all the lines (which are always red)
for coords in st.session_state.lines:
    folium.PolyLine(
        locations=[(coord[1], coord[0]) for coord in coords],
        color="red",  # All lines are red
        weight=3
    ).add_to(m)

# Display the total pipe length in the sidebar
st.sidebar.subheader("Total Pipe Length")
st.sidebar.write(f"{st.session_state.total_pipe_length:.2f} meters")

# Render the updated map
st_folium(m, width=725, height=500)
