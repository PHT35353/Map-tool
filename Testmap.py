import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Initialize the Streamlit app
st.title("Map Tool for Pipe Design with Distance Calculation")

# Instructions
st.write("""
1. Select an area of interest on the map.
2. Click to add dots on the map representing places to pipe from or to.
3. Draw lines between these dots (pipes), and the tool will give the distances in real-world scale.
""")

# Create a base map centered at a default location with proper attribution
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13, tiles='Stamen Terrain', 
               attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.")

# Initialize data storage for coordinates
selected_points = []
line_segments = []

# Interactive Folium map
map_data = st_folium(m, width=700, height=500)

# Allow user to select dots (places)
if map_data and map_data['last_clicked']:
    last_click = map_data['last_clicked']
    lat, lon = last_click['lat'], lon = last_click['lng']
    
    # Append the selected point
    selected_points.append((lat, lon))
    
    # Add a marker for the selected point
    folium.Marker([lat, lon], popup=f"Place {len(selected_points)}").add_to(m)

    # Refresh the map with updated points
    st.write(f"Point {len(selected_points)} added at: Latitude: {lat}, Longitude: {lon}")

# Allow user to draw lines between the points (pipes)
if len(selected_points) > 1:
    # Ask user to connect two points
    st.write("Select two points to connect with a pipe:")
    point1 = st.selectbox("Point 1", range(1, len(selected_points) + 1))
    point2 = st.selectbox("Point 2", range(1, len(selected_points) + 1))

    # Ensure the selected points are different
    if point1 != point2:
        # Get the coordinates for the two points
        coord1 = selected_points[point1 - 1]
        coord2 = selected_points[point2 - 1]

        # Draw a line between the points
        folium.PolyLine(locations=[coord1, coord2], color='blue', weight=2.5).add_to(m)

        # Calculate the distance between the two points
        distance = geodesic(coord1, coord2).meters
        st.write(f"Distance between Point {point1} and Point {point2}: {distance:.2f} meters")

        # Store the line segment for reference
        line_segments.append((coord1, coord2, distance))

# Re-render the map with new markers and lines
st_folium(m, width=700, height=500)

# Display the width and height of the selected area (bounding box)
if map_data and 'bounds' in map_data and map_data['bounds']:
    bounds = map_data['bounds']
    north_east = bounds['northeast']
    south_west = bounds['southwest']

    # Calculate the width and height of the bounding box in meters
    width = geodesic((north_east['lat'], south_west['lng']), (north_east['lat'], north_east['lng'])).meters
    height = geodesic((north_east['lat'], south_west['lng']), (south_west['lat'], south_west['lng'])).meters

    st.write(f"Selected Area: Width = {width:.2f} meters, Height = {height:.2f} meters")

# List all the pipe connections and their distances
if line_segments:
    st.write("Pipe Connections and Distances:")
    for idx, (p1, p2, dist) in enumerate(line_segments):
        st.write(f"Pipe {idx + 1}: From {p1} to {p2}, Distance: {dist:.2f} meters")
