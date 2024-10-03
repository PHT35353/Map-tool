import streamlit as st
import pydeck as pdk
import numpy as np
import json

# Set your Mapbox access token
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# Set the Mapbox access token
pdk.settings.mapbox_api_access_token = MAPBOX_ACCESS_TOKEN

# Initialize state variables
if 'lines' not in st.session_state:
    st.session_state.lines = []
if 'points' not in st.session_state:
    st.session_state.points = []
if 'color' not in st.session_state:
    st.session_state.color = [255, 0, 0]  # Default color (red)

# Function to calculate distance in meters
def calculate_distance(point1, point2):
    lat1, lon1 = np.radians(point1)
    lat2, lon2 = np.radians(point2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    r = 6371000  # Radius of Earth in meters
    return c * r

# Function to handle line drawing by clicking on the map
def add_line(start, end):
    st.session_state.lines.append((start, end))

# Function to clear lines
def clear_lines():
    st.session_state.lines = []

# Streamlit layout
st.title("Industrial Piping Tool")

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    
    # Input for adding points
    start_point = st.text_input("Start Point (latitude,longitude)", "37.7749,-122.4194")
    end_point = st.text_input("End Point (latitude,longitude)", "37.7750,-122.4183")
    
    if st.button("Add Line"):
        try:
            start_coords = [float(coord) for coord in start_point.split(",")]
            end_coords = [float(coord) for coord in end_point.split(",")]
            add_line(start_coords, end_coords)
            distance = calculate_distance(start_coords, end_coords)
            st.success(f"Line added! Distance: {distance:.2f} meters")
        except ValueError:
            st.error("Please enter valid latitude and longitude values.")
    
    # Input for adding landmarks
    landmark_input = st.text_input("Add Landmark (latitude,longitude)", "37.7750,-122.4190")
    if st.button("Add Landmark"):
        try:
            landmark_coords = [float(coord) for coord in landmark_input.split(",")]
            st.session_state.points.append({"longitude": landmark_coords[1], "latitude": landmark_coords[0]})
            st.success("Landmark added!")
        except ValueError:
            st.error("Please enter valid latitude and longitude values.")

    # Option to clear lines
    if st.button("Clear Lines"):
        clear_lines()
        st.success("All lines cleared.")

    # Color customization
    st.subheader("Customize Line Color")
    red = st.slider("Red", 0, 255, 255)
    green = st.slider("Green", 0, 255, 0)
    blue = st.slider("Blue", 0, 255, 0)
    st.session_state.color = [red, green, blue]

# Map configuration
initial_view_state = pdk.ViewState(
    latitude=37.7749,  # Default latitude
    longitude=-122.4194,  # Default longitude
    zoom=13,
    pitch=45,  # Pitch for 3D view
)

# Layer for lines
line_layers = [
    pdk.Layer(
        "PathLayer",
        data=[
            {
                "path": [[line[0][1], line[0][0]], [line[1][1], line[1][0]]],  # [longitude, latitude]
                "color": st.session_state.color,
                "width": 5,
            }
            for line in st.session_state.lines
        ],
        get_color="color",
        width_scale=20,
        width_min_pixels=5,
    )
]

# Layer for points
point_layers = [
    pdk.Layer(
        "ScatterplotLayer",
        data=st.session_state.points,
        get_position="[longitude, latitude]",
        get_color="[255, 0, 0, 160]",
        get_radius=200,
        pickable=True,
    )
]

# Create the deck
try:
    r = pdk.Deck(
        layers=line_layers + point_layers,
        initial_view_state=initial_view_state,
        map_style="mapbox://styles/mapbox/satellite-v9",  # Satellite view
    )
except Exception as e:
    st.error(f"Error creating the deck: {e}")

# Display the map
st.pydeck_chart(r)

# JavaScript function to handle click events for drawing lines
st.markdown(
    """
    <script>
    const deck = document.querySelector('deck-gl');
    deck.addEventListener('click', function (e) {
        const coords = e.lngLat;
        // Assuming lines are added on click
        if (window.streamlitApp) {
            window.streamlitApp.addLine([coords.lat, coords.lng]);
        }
    });
    </script>
    """,
    unsafe_allow_html=True
)
