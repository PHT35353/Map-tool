import streamlit as st
from streamlit_leaflet import st_leaflet
import numpy as np
import pandas as pd

# Function to calculate distance in meters
def calculate_distance(point1, point2):
    # Haversine formula to calculate distance between two points
    lat1, lon1 = np.radians(point1)
    lat2, lon2 = np.radians(point2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    r = 6371000  # Radius of Earth in meters
    return c * r

# Initialize session state variables
if 'lines' not in st.session_state:
    st.session_state.lines = []
if 'points' not in st.session_state:
    st.session_state.points = []
if 'color' not in st.session_state:
    st.session_state.color = [255, 0, 0]  # Default color (red)

# Sidebar for controls
st.sidebar.title("Controls")

# Map settings
st.sidebar.subheader("Map Settings")
zoom_level = st.sidebar.slider("Zoom Level", 1, 18, 13)
lat = st.sidebar.number_input("Latitude", value=37.7749)
lon = st.sidebar.number_input("Longitude", value=-122.4194)

# Input for adding landmarks
landmark_input = st.sidebar.text_input("Add Landmark (latitude,longitude)", "37.7750,-122.4190")
if st.sidebar.button("Add Landmark"):
    try:
        landmark_coords = [float(coord) for coord in landmark_input.split(",")]
        st.session_state.points.append({
            "latitude": landmark_coords[0],
            "longitude": landmark_coords[1],
            "name": f"Landmark at {landmark_input}"
        })
        st.sidebar.success("Landmark added!")
    except ValueError:
        st.sidebar.error("Please enter valid latitude and longitude values.")

# Color customization
st.sidebar.subheader("Customize Line Color")
red = st.sidebar.slider("Red", 0, 255, 255)
green = st.sidebar.slider("Green", 0, 255, 0)
blue = st.sidebar.slider("Blue", 0, 255, 0)
st.session_state.color = [red, green, blue]

# Leaflet map
st.subheader("Industrial Piping Tool")
leaflet_map = st_leaflet(
    center={"lat": lat, "lon": lon},
    zoom=zoom_level,
    tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    height=500,
)

# Handling line drawing on the map
if leaflet_map["last_event"]:
    event = leaflet_map["last_event"]
    if event["event"] == "click":
        coords = event["latlng"]
        if len(st.session_state.lines) % 2 == 0:
            st.session_state.lines.append([coords["lat"], coords["lng"]])
            st.sidebar.success(f"Start Point Added: {coords}")
        else:
            st.session_state.lines[-1].append([coords["lat"], coords["lng"]])
            st.sidebar.success(f"End Point Added: {coords}")

# Drawing lines on the map
if len(st.session_state.lines) > 0:
    for line in st.session_state.lines:
        if len(line) == 2:  # Ensure we have a start and end point
            st_leaflet.add_polyline(
                locations=line,
                color=f'#{red:02x}{green:02x}{blue:02x}',  # Convert RGB to Hex
                weight=5,
            )
            distance = calculate_distance(line[0], line[1])
            st.sidebar.success(f"Line Distance: {distance:.2f} meters")

# Display landmarks on the map
for point in st.session_state.points:
    st_leaflet.add_marker(
        location={"lat": point["latitude"], "lon": point["longitude"]},
        popup=point["name"],
        color='blue'
    )
