import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Set up a title for the app
st.title("Map-Based Piping Layout Tool with Region Selection")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle (region selection).
2. Place points (representing facilities) within the selected region.
3. Draw lines (pipes) between the points and calculate distances.
4. Remove points or lines.
""")

# Set the starting location and zoom to the Netherlands
default_location = [52.3676, 4.9041]  # Amsterdam, Netherlands
zoom_start = 13

# Create a Folium map with Mapbox Satellite layer
m = folium.Map(location=default_location, zoom_start=zoom_start)

# Add Mapbox Satellite layer (replace this with your valid token)
tile_url = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"
folium.TileLayer(tiles=tile_url, attr='Mapbox').add_to(m)

# Add drawing tool for selecting a region on the map (rectangle)
draw = folium.plugins.Draw(export=True, draw_options={'rectangle': True, 'polyline': False, 'polygon': False, 'circle': False})
draw.add_to(m)

# Store selected points and lines
points = []
lines = []
distances = []

# Sidebar to manage the map interactions
st.sidebar.title("Map Interactions")

# Define a place for storing selected region bounds
selected_region_bounds = st.sidebar.text_area("Selected Region Bounds", "No region selected yet")

# Render the map
output = st_folium(m, width=725)

# Check if a rectangle (region) was drawn
if output and output['all_drawings']:
    for shape in output['all_drawings']:
        if shape['geometry']['type'] == 'Polygon':
            coords = shape['geometry']['coordinates'][0]
            selected_region_bounds = f"SW: {coords[0]} NE: {coords[2]}"
            st.sidebar.success(f"Region selected: {selected_region_bounds}")

# Place points within the selected region
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

if st.sidebar.button("Place Facility"):
    point = [latitude, longitude]
    # You might want to check if point lies within the selected region bounds.
    points.append(point)
    folium.Marker(location=point, tooltip=f"Facility {len(points)}").add_to(m)
    st.success(f"Placed facility at {point}")

# Allow user to connect points with lines (pipes)
if len(points) > 1:
    start_index = st.sidebar.selectbox("Select Starting Point", range(1, len(points) + 1))
    end_index = st.sidebar.selectbox("Select Ending Point", range(1, len(points) + 1))
    if st.sidebar.button("Connect Points"):
        start_point = points[start_index - 1]
        end_point = points[end_index - 1]
        folium.PolyLine(locations=[start_point, end_point], color="blue", weight=2.5).add_to(m)
        distance = geodesic(start_point, end_point).meters
        distances.append(distance)
        lines.append([start_point, end_point])
        st.sidebar.write(f"Distance between Point {start_index} and Point {end_index}: {distance:.2f} meters")

# Display all pipe distances
st.sidebar.subheader("Pipe Distances")
for i, distance in enumerate(distances, start=1):
    st.sidebar.write(f"Pipe {i}: {distance:.2f} meters")

# Remove points or lines
if st.sidebar.button("Remove Last Facility"):
    if points:
        removed_point = points.pop()
        st.warning(f"Removed facility at {removed_point}")
    else:
        st.warning("No more facilities to remove!")

if st.sidebar.button("Remove Last Pipe"):
    if lines:
        removed_line = lines.pop()
        removed_distance = distances.pop()
        st.warning(f"Removed pipe with distance {removed_distance:.2f} meters")
    else:
        st.warning("No more pipes to remove!")

# Render the updated map in the Streamlit app
st_data = st_folium(m, width=725)
