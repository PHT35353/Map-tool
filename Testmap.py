import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Streamlit app title
st.title("Accurate Distance Calculator Using Leaflet and Geodesic Distance")

# Sidebar for displaying information and actions
st.sidebar.title("Selected Points & Distances")

# Initialize a new map with dynamic center and zoom
def initialize_map(center, zoom):
    return folium.Map(location=center, zoom_start=zoom)

# Function to calculate accurate geodesic distance
def calculate_geodesic_distance(locations):
    distances = []
    for i in range(1, len(locations)):
        coords_1 = (locations[i-1]['lat'], locations[i-1]['lng'])
        coords_2 = (locations[i]['lat'], locations[i]['lng'])  # Fixed line
        distance_km = geodesic(coords_1, coords_2).kilometers
        if distance_km < 1:
            distance = f"{distance_km * 1000:.2f} meters"
        else:
            distance = f"{distance_km:.2f} km"
        distances.append(distance)
    return distances

# Add markers and lines to the map
def draw_lines_and_markers(map_obj, locations, distances):
    for i in range(len(locations)):
        point = locations[i]
        
        # Add markers (dots) at clicked points
        folium.Marker([point['lat'], point['lng']], popup=f"Point {i+1}").add_to(map_obj)
        
        # Draw line and show distance after two points
        if i > 0:
            point1 = locations[i-1]
            point2 = point
            
            # Draw line between points
            folium.PolyLine(locations=[[point1['lat'], point1['lng']], [point2['lat'], point2['lng']]],
                            color="blue", weight=2.5, opacity=1).add_to(map_obj)
            
            # Show distance on the map
            midpoint = [(point1['lat'] + point2['lat']) / 2, (point1['lng'] + point2['lng']) / 2]
            folium.Marker(midpoint, 
                          icon=folium.DivIcon(html=f"<div style='font-size: 12px; color: black;'>{distances[i-1]}</div>")
                         ).add_to(map_obj)

# Store session state for previous clicks, center, and zoom
if 'last_clicked_coords' not in st.session_state:
    st.session_state['last_clicked_coords'] = None  # To track the last click coordinates

if 'all_clicks' not in st.session_state:
    st.session_state['all_clicks'] = []  # To track all clicked points

# Set initial map state (center and zoom)
if 'map_center' not in st.session_state:
    st.session_state['map_center'] = [52.52, 13.405]  # Initial center (Berlin)
if 'map_zoom' not in st.session_state:
    st.session_state['map_zoom'] = 10  # Initial zoom level

# Initialize the map with stored center and zoom
m = initialize_map(st.session_state['map_center'], st.session_state['map_zoom'])

# Draw markers and lines from previous clicks
if len(st.session_state['all_clicks']) > 0:
    distances = calculate_geodesic_distance(st.session_state['all_clicks'])
    draw_lines_and_markers(m, st.session_state['all_clicks'], distances)

# Collect map data (user clicks and map movements)
location_data = st_folium(m, height=500, width=700)

# Process new clicks on the map
if location_data and location_data.get('last_clicked') is not None:
    lat_lng = location_data['last_clicked']
    
    # Check if the clicked coordinates are different from the last click
    if st.session_state['last_clicked_coords'] is None or \
       (lat_lng['lat'] != st.session_state['last_clicked_coords']['lat'] or \
        lat_lng['lng'] != st.session_state['last_clicked_coords']['lng']):
        
        # Update the last clicked coordinates
        st.session_state['last_clicked_coords'] = lat_lng
        
        # Store the clicked location in session state
        st.session_state['all_clicks'].append({'lat': lat_lng['lat'], 'lng': lat_lng['lng']})
        
        # Redraw the map with updated markers and lines
        distances = calculate_geodesic_distance(st.session_state['all_clicks'])
        draw_lines_and_markers(m, st.session_state['all_clicks'], distances)

# Capture the current map center and zoom level
if location_data and location_data.get('bounds') is not None:
    bounds = location_data['bounds']
    
    # Only update if the bounds have 'north', 'south', 'east', and 'west'
    if 'north' in bounds and 'south' in bounds and 'east' in bounds and 'west' in bounds:
        new_center_lat = (bounds['north'] + bounds['south']) / 2
        new_center_lng = (bounds['east'] + bounds['west']) / 2
        st.session_state['map_center'] = [new_center_lat, new_center_lng]
        st.session_state['map_zoom'] = location_data.get('zoom', st.session_state['map_zoom'])

# Show the selected points in the sidebar
if len(st.session_state['all_clicks']) > 0:
    st.sidebar.subheader("Selected Points:")
    for i, point in enumerate(st.session_state['all_clicks'], start=1):
        st.sidebar.markdown(f"**Point {i}:** ({point['lat']:.5f}, {point['lng']:.5f})")

# Calculate and display distances if at least two points are selected
if len(st.session_state['all_clicks']) >= 2:
    distances = calculate_geodesic_distance(st.session_state['all_clicks'])
    st.sidebar.subheader("Distances Between Points:")
    for i, dist in enumerate(distances, start=1):
        st.sidebar.markdown(f"**Point {i} to Point {i+1}:** {dist}")

# Clear Points button in the sidebar
if st.sidebar.button("Clear Points"):
    st.session_state['all_clicks'] = []
    st.session_state['last_clicked_coords'] = None
    st.sidebar.write("Points cleared. Select new locations.")
