import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Streamlit app title
st.title("Accurate Distance Calculator Using Leaflet and Geodesic Distance")

# Sidebar for displaying information and actions
st.sidebar.title("Selected Points & Distances")

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
    for i, point in enumerate(locations):
        point_color = point['color'].strip()

        folium.CircleMarker(
            location=[point['lat'], point['lng']],
            radius=10,
            popup=f"{point['name']}",
            color=point_color,  # Border color
            fill=True,
            fill_color=point_color,  # Fill color
            fill_opacity=0.9
        ).add_to(map_obj)

    # Draw lines between every pair of points and calculate distances
    if len(locations) > 1:
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                point1 = locations[i]
                point2 = locations[j]

                folium.PolyLine(
                    locations=[[point1['lat'], point1['lng']], [point2['lat'], point2['lng']]],
                    color="blue", weight=2.5, opacity=1
                ).add_to(map_obj)

                distance = calculate_distance((point1['lat'], point1['lng']), (point2['lat'], point2['lng']))
                distances.append(f"{point1['name']} to {point2['name']}: {distance}")

    return distances

# Set initial session state for map center, zoom, and clicks
if 'map_center' not in st.session_state:
    st.session_state['map_center'] = [52.1, 5.3]  # Initial map center for the Netherlands
if 'map_zoom' not in st.session_state:
    st.session_state['map_zoom'] = 7  # Initial zoom level
if 'all_clicks' not in st.session_state:
    st.session_state['all_clicks'] = []  # To track all clicked points

# Initialize the map with stored session state center and zoom
m = folium.Map(location=st.session_state['map_center'], zoom_start=st.session_state['map_zoom'])

# Draw existing points and lines
if len(st.session_state['all_clicks']) > 0:
    distances_in_sidebar = draw_lines_and_markers(m, st.session_state['all_clicks'])

# Display the map and capture user interaction (click, move, zoom)
location_data = st_folium(m, height=500, width=700)

# If the map has moved or zoomed, update the session state
if location_data and location_data.get('center') and location_data.get('zoom'):
    new_center = [location_data['center']['lat'], location_data['center']['lng']]
    new_zoom = location_data['zoom']

    # Only update session state if the map's center or zoom has changed
    if new_center != st.session_state['map_center'] or new_zoom != st.session_state['map_zoom']:
        st.session_state['map_center'] = new_center
        st.session_state['map_zoom'] = new_zoom

# If a new point is clicked, capture it and add to session state
if location_data and location_data.get('last_clicked'):
    lat_lng = location_data['last_clicked']

    # Get point name and color from user input
    point_name = st.sidebar.text_input("Name for this point", f"Point {len(st.session_state['all_clicks']) + 1}")
    point_color = st.sidebar.color_picker("Select color for this point", "#3186cc")

    if st.sidebar.button("Add Point"):
        # Store the clicked location
        st.session_state['all_clicks'].append({
            'lat': lat_lng['lat'],
            'lng': lat_lng['lng'],
            'name': point_name,
            'color': point_color
        })

# Sidebar section for displaying and removing points
if len(st.session_state['all_clicks']) > 0:
    st.sidebar.subheader("Selected Points:")
    for i, point in enumerate(st.session_state['all_clicks'], start=1):
        col1, col2 = st.sidebar.columns([3, 1])
        col1.markdown(f"**{point['name']}:** ({point['lat']:.5f}, {point['lng']:.5f})")

        if col2.button(f"Remove Point {i}", key=f"remove_{i}"):
            del st.session_state['all_clicks'][i]
            break  # To avoid list mutation issues during iteration

# Clear all points button
if st.sidebar.button("Clear All Points"):
    st.session_state['all_clicks'] = []
