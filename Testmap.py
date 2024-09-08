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
def draw_lines_and_markers(map_obj, locations, lines_to_remove):
    distances = []
    # Add markers (dots) for each clicked point
    for i, point in enumerate(locations):
        folium.Marker([point['lat'], point['lng']], popup=f"Point {i+1}").add_to(map_obj)
    
    # Draw lines between every pair of points and calculate distances
    if len(locations) > 1:
        for i in range(len(locations)):
            for j in range(i+1, len(locations)):
                if (i, j) in lines_to_remove:
                    continue  # Skip drawing lines that were removed

                point1 = locations[i]
                point2 = locations[j]
                
                # Draw line between point1 and point2
                folium.PolyLine(
                    locations=[[point1['lat'], point1['lng']], [point2['lat'], point2['lng']]],
                    color="blue", weight=2.5, opacity=1
                ).add_to(map_obj)
                
                # Calculate and save distance
                distance = calculate_distance((point1['lat'], point1['lng']), (point2['lat'], point2['lng']))
                distances.append({'i': i, 'j': j, 'label': f"Point {i+1} to Point {j+1}: {distance}"})
                
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

# Track the lines that are removed
if 'removed_lines' not in st.session_state:
    st.session_state['removed_lines'] = set()  # Set of tuples (i, j) for lines removed

# Set initial map state (center and zoom) for the Netherlands
if 'map_center' not in st.session_state:
    st.session_state['map_center'] = [52.1, 5.3]  # Center the map in the Netherlands
if 'map_zoom' not in st.session_state:
    st.session_state['map_zoom'] = 7  # Initial zoom level suitable for the Netherlands

# Toggle fullscreen state
if 'fullscreen' not in st.session_state:
    st.session_state['fullscreen'] = False  # Track whether the map is fullscreen

# Search by Coordinates
st.sidebar.subheader("Search by Coordinates")
lat = st.sidebar.text_input("Enter Latitude", "")
lng = st.sidebar.text_input("Enter Longitude", "")

# If both latitude and longitude are provided, update the map center
if lat and lng:
    try:
        lat, lng = float(lat), float(lng)
        st.session_state['map_center'] = [lat, lng]
        st.session_state['map_zoom'] = 14  # Zoom in to show the location clearly
    except ValueError:
        st.warning("Please enter valid numeric coordinates for both latitude and longitude.")

# Initialize the map with stored center and zoom
m = initialize_map(st.session_state['map_center'], st.session_state['map_zoom'])

# Draw markers and lines from previous clicks, and collect distances
distances_in_sidebar = []
if len(st.session_state['all_clicks']) > 0:
    distances_in_sidebar = draw_lines_and_markers(m, st.session_state['all_clicks'], st.session_state['removed_lines'])

# Collect map data (user clicks and map movements)
map_height = 500 if not st.session_state['fullscreen'] else 800  # Adjust map size based on fullscreen
location_data = st_folium(m, height=map_height, width=700)

# Fullscreen toggle button
if st.button("Enlarge/Reduce Map"):
    st.session_state['fullscreen'] = not st.session_state['fullscreen']  # Toggle fullscreen state

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
        distances_in_sidebar = draw_lines_and_markers(m, st.session_state['all_clicks'], st.session_state['removed_lines'])

# Capture the current map zoom and center after zooming/panning
if location_data and 'center' in location_data and 'zoom' in location_data:
    # Save the current center and zoom after map interaction
    st.session_state['map_center'] = [location_data['center']['lat'], location_data['center']['lng']]
    st.session_state['map_zoom'] = location_data['zoom']

# Sidebar section for removing points
if len(st.session_state['all_clicks']) > 0:
    st.sidebar.subheader("Selected Points:")
    for i, point in enumerate(st.session_state['all_clicks'], start=1):
        col1, col2 = st.sidebar.columns([3, 1])
        col1.markdown(f"**Point {i}:** ({point['lat']:.5f}, {point['lng']:.5f})")
        
        # Add a "Remove" button next to each point
        if col2.button(f"Remove Point {i}", key=f"remove_{i}"):
            # Remove the point from the list
            st.session_state['all_clicks'].pop(i)
            
            # Re-render the map and sidebar without the removed point
            distances_in_sidebar = draw_lines_and_markers(m, st.session_state['all_clicks'], st.session_state['removed_lines'])
            break  # Break the loop to prevent issues with rendering the sidebar mid-change

# Display the distances between all points in the sidebar and allow removal
if distances_in_sidebar:
    st.sidebar.subheader("Distances Between Points:")
    for distance in distances_in_sidebar:
        col1, col2 = st.sidebar.columns([3, 1])
        col1.markdown(distance['label'])
        
        # Add a "Remove Line" button next to each distance
        if col2.button(f"Remove Line {distance['i']+1}-{distance['j']+1}", key=f"remove_line_{distance['i']}_{distance['j']}"):
            # Add the removed line to the set
            st.session_state['removed_lines'].add((distance['i'], distance['j']))
            
            # Re-render the map and sidebar without the removed line
            distances_in_sidebar = draw_lines_and_markers(m, st.session_state['all_clicks'], st.session_state['removed_lines'])
            break  # Break to prevent issues with rendering the sidebar mid-change

# Clear Points button in the sidebar
if st.sidebar.button("Clear All Points"):
    st.session_state['all_clicks'] = []
    st.session_state['last_clicked_coords'] = None
    st.session_state['removed_lines'] = set()  # Clear the removed lines as well
    st.sidebar.write("All points cleared. Select new locations.")
