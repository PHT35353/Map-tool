import streamlit as st
import json
import numpy as np

# Initialize session state variables
if 'lines' not in st.session_state:
    st.session_state.lines = []
if 'color' not in st.session_state:
    st.session_state.color = [255, 0, 0]  # Default color (red)

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

# Sidebar for controls
st.sidebar.title("Controls")
st.sidebar.subheader("Map Settings")
zoom_level = st.sidebar.slider("Zoom Level", 1, 18, 13)
lat = st.sidebar.number_input("Latitude", value=37.7749)
lon = st.sidebar.number_input("Longitude", value=-122.4194)

# Color customization
st.sidebar.subheader("Customize Line Color")
red = st.sidebar.slider("Red", 0, 255, 255)
green = st.sidebar.slider("Green", 0, 255, 0)
blue = st.sidebar.slider("Blue", 0, 255, 0)
st.session_state.color = [red, green, blue]

# Display the map using Leaflet
st.subheader("Industrial Piping Tool")

# Include JavaScript and HTML for Leaflet map with drawing capability
st.markdown(
    f"""
    <style>
    #map {{
        height: 500px;
    }}
    </style>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-draw/dist/leaflet.draw.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet-draw/dist/leaflet.draw.css"/>
    <script>
    // Initialize the Leaflet map
    var map = L.map('map').setView([{lat}, {lon}], {zoom_level});
    
    // Add Mapbox tile layer
    L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{{z}}/{{x}}/{{y}}?access_token=pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw', {{
        maxZoom: 18,
        tileSize: 512,
        zoomOffset: -1
    }}).addTo(map);
    
    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    
    var drawControl = new L.Control.Draw({{
        edit: {{
            featureGroup: drawnItems,
        }},
        draw: {{
            polyline: {{
                shapeOptions: {{
                    color: 'rgb({red},{green},{blue})'
                }}
            }},
            polygon: true,
            circle: false,
            rectangle: false,
            marker: false,
        }}
    }});
    map.addControl(drawControl);

    map.on('draw:created', function (e) {{
        var layer = e.layer;
        drawnItems.addLayer(layer);
        var coordinates = layer.getLatLngs();

        // Send coordinates back to Streamlit
        const coords = coordinates.map(latlng => [latlng.lat, latlng.lng]);
        
        // Store the coordinates in a hidden input field to be captured by Streamlit
        window.streamlitApp.send_coords(coords);
    }});
    </script>
    """,
    unsafe_allow_html=True
)

# Display the drawn lines on the map
if st.session_state.lines:
    for line in st.session_state.lines:
        st.markdown(f"<script>map.addPolyline({json.dumps(line)}, {json.dumps(st.session_state.color)});</script>", unsafe_allow_html=True)

# Function to receive coordinates
def send_coords(coords):
    if coords:
        st.session_state.lines.append(coords)
        st.success(f"Line added! Coordinates: {coords}")

# Register the function
st.experimental_singleton(send_coords)
