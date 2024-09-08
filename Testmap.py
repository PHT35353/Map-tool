import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Streamlit app title
st.title("Pipe Distance Calculator Using Leaflet and OpenStreetMap")

# Initialize the map with a center point
m = folium.Map(location=[52.52, 13.405], zoom_start=10)  # Centered on Berlin, Germany

# Instructions
st.markdown("Click on two locations on the map to calculate the distance between them.")

# Add markers based on user input (clicks)
location_data = st_folium(m, height=500, width=700)

# Function to calculate distance between two points
def calculate_distance(locations):
    if len(locations) < 2:
        return "Please select two points on the map."
    
    coords_1 = (locations[0]['lat'], locations[0]['lng'])
    coords_2 = (locations[1]['lat'], locations[1]['lng'])
    distance = geodesic(coords_1, coords_2).km
    return f"Distance between selected points: {distance:.2f} km"

# Collect the locations from the user's clicks
if location_data:
    if 'all_clicks' not in st.session_state:
        st.session_state['all_clicks'] = []

    # Get the latest click
    if location_data['last_clicked'] is not None:
        lat_lng = location_data['last_clicked']
        st.session_state['all_clicks'].append({'lat': lat_lng['lat'], 'lng': lat_lng['lng']})

    # Display the selected points
    if len(st.session_state['all_clicks']) > 0:
        st.write(f"Selected points: {st.session_state['all_clicks']}")

    # Calculate and display the distance if two points are selected
    if len(st.session_state['all_clicks']) >= 2:
        result = calculate_distance(st.session_state['all_clicks'][:2])  # Only use the first two points
        st.write(result)

# Button to clear selected points
if st.button("Clear Points"):
    st.session_state['all_clicks'] = []
    st.write("Points cleared. Select new locations.")

