import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Streamlit app title
st.title("Accurate Distance Calculator Using Leaflet and Geodesic Distance")

# Sidebar for displaying information and actions
st.sidebar.title("Selected Points & Distances")

# Initialize a new map with a center point (Berlin)
def initialize_map():
    return folium.Map(location=[52.52, 13.405], zoom_start=10)

# Function to calculate accurate geodesic distance
def calculate_geodesic_distance(locations):
    distances = []
    for i in range(1, len(locations)):
        coords_1 = (locations[i-1]['lat'], locations[i-1]['lng'])
        coords_2 = (locations[i]['lat'], locations[i]['lng'])
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

# Store session state for previous clicks
if 'last_clicked_coords' not in st.session_state:
    st.session_state['last_clicked_coords'] = None  # To track the last click coordinates

if 'all_clicks' not in st.session_state:
    st.session_state['all_clicks'] = []  # To track all clicked points

# Re-initialize the map (to ensure persistence of markers and lines)
m = initialize_map()

# Draw markers and lines from previous clicks
if len(st.session_state['all_clicks']) > 0:
    distances = calculate_geodesic_distance(st.session_state['all_clicks'])
    draw_lines_and_markers(m, st.session_state['all_clicks'], distances)

# Collect map data (user clicks)
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
        if len(st.session_state['all_clicks']) >= 2:
            distances = calculate_geodesic_distance(st.session_state['all_clicks'])
            draw_lines_and_markers(m, st.session_state['all_clicks'], distances)

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
