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

# Function to calculate geodesic distance between two points
def calculate_distance(coords_1, coords_2):
    distance_km = geodesic(coords_1, coords_2).kilometers
    if distance_km < 1:
        return f"{distance_km * 1000:.2f} meters"
    else:
        return f"{distance_km:.2f} km"

# Add markers and lines to the map
def draw_lines_and_markers(map_obj, locations):
    distances = []
    # Add markers (dots) for each clicked point
    for i, point in enumerate(locations):
        folium.Marker([point['lat'], point['lng']], popup=f"Point {i+1}").add_to(map_obj)
    
    # Draw lines between every pair of points and calculate distances
    if len(locations) > 1:
        for i in range(len(locations)):
            for j in range(i+1, len(locations)):
                point1 = locations[i]
                point2 = locations[j]
                
                # Draw line between point1 and point2
                folium.PolyLine(
                    locations=[[point1['lat'], point1['lng']], [point2['lat'], point2['lng']]],
                    color="blue", weight=2.5, opacity=1
                ).add_to(map_obj)
                
                # Calculate and save distance
                distance = calculate_distance((point1['lat'], point1['lng']), (point2['lat'], point2['lng']))
                distances.append(f"Point {i+1} to Point {j+1}: {distance}")
                
                # Show distance at the midpoint of the line
                midpoint = [(point1['lat'] + point2['lat']) / 2, (point1['lng'] + point2['lng']) / 2]
                folium.Marker(midpoint, 
                              icon=folium.DivIcon(html=f"<div style='font-size: 12px; color: black;'>{distance}</div>")
                             ).add_to(map_obj)
    
    return distances

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

# Draw markers and lines from previous clicks, and collect distances
distances_in_sidebar = []
if len(st.session_state['all_clicks']) > 0:
    distances_in_sidebar = draw_lines_and_markers(m, st.session_state['all_clicks'])

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
        
        # Update the map center only when a point is clicked
        st.session_state['map_center'] = [lat_lng['lat'], lat_lng['lng']]
        
        # Redraw the map with updated markers and lines, and collect distances
        distances_in_sidebar = draw_lines_and_markers(m, st.session_state['all_clicks'])

# Capture the current map zoom and center after zooming/panning
if location_data and 'center' in location_data and 'zoom' in location_data:
    # Save the current center and zoom after map interaction
    st.session_state['map_center'] = [location_data['center']['lat'], location_data['center']['lng']]
    st.session_state['map_zoom'] = location_data['zoom']

# Show the selected points in the sidebar
if len(st.session_state['all_clicks']) > 0:
    st.sidebar.subheader("Selected Points:")
    for i, point in enumerate(st.session_state['all_clicks'], start=1):
        st.sidebar.markdown(f"**Point {i}:** ({point['lat']:.5f}, {point['lng']:.5f})")

# Display the distances between all points in the sidebar
if distances_in_sidebar:
    st.sidebar.subheader("Distances Between Points:")
    for distance_info in distances_in_sidebar:
        st.sidebar.markdown(distance_info)

# Clear Points button in the sidebar
if st.sidebar.button("Clear Points"):
    st.session_state['all_clicks'] = []
    st.session_state['last_clicked_coords'] = None
    st.sidebar.write("Points cleared. Select new locations.")
