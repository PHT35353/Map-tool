import streamlit as st
import streamlit.components.v1 as components
import requests

# Set up a title for the app
st.title("Interactive Map Tool with Individual Colors, Names, and Landmark Relations")

# Add instructions and explain color options
st.markdown("""
This tool allows you to:
1. Draw rectangles (polygons), lines, and markers (landmarks) on the map.
2. Assign names and choose specific colors for each feature individually upon creation.
3. Display distances for lines and dimensions for polygons both on the map and in the sidebar.
4. Show relationships between landmarks and lines (e.g., a line belongs to two landmarks).

**Available Colors**:
- Named colors: `red`, `blue`, `green`, `yellow`, `purple`, `cyan`, `pink`, `orange`, `black`, `white`, `gray`
- Hex colors: `#FF0000` (red), `#00FF00` (green), `#0000FF` (blue), `#FFFF00` (yellow), `#800080` (purple), `#00FFFF` (cyan), `#FFC0CB` (pink), `#FFA500` (orange), `#000000` (black), `#FFFFFF` (white), `#808080` (gray)
""")

# Sidebar to manage the map interactions
st.sidebar.title("Map Controls")

# Default location set to Amsterdam, Netherlands
default_location = [52.3676, 4.9041]

# Input fields for latitude and longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Search bar for address search
address_search = st.sidebar.text_input("Search for address (requires internet connection)")

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

# Sidebar section for displaying measurements
st.sidebar.title("Measurements")
measurement_display = st.sidebar.empty()  # Placeholder for the measurements

# Mapbox GL JS API token
mapbox_access_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# HTML and JS for Mapbox with Mapbox Draw plugin to add drawing functionalities
mapbox_map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Mapbox GL JS Drawing Tool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script src="https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.css" rel="stylesheet" />
    <script src="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.3.0/mapbox-gl-draw.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.3.0/mapbox-gl-draw.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/@turf/turf/turf.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        #map {{
            position: absolute;
            top: 0;
            bottom: 0;
            width: 100%;
        }}
        .mapboxgl-ctrl {{
            margin: 10px;
        }}
    </style>
</head>
<body>
<div id="map"></div>
<script>
    mapboxgl.accessToken = '{mapbox_access_token}';
    
    const map = new mapboxgl.Map({{
        container: 'map',
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: [{longitude}, {latitude}],
        zoom: 13,
        pitch: 45, // For 3D effect
        bearing: 0, // Rotation angle
        antialias: true
    }});

    // Add map controls for zoom, rotation, and fullscreen
    map.addControl(new mapboxgl.NavigationControl());
    map.addControl(new mapboxgl.FullscreenControl());

    // Enable rotation and pitch adjustments using right-click
    map.dragRotate.enable();
    map.touchZoomRotate.enableRotation();

    // Add the Draw control for drawing polygons, markers, lines, etc.
    const Draw = new MapboxDraw({{
        displayControlsDefault: false,
        controls: {{
            polygon: true,
            line_string: true,
            point: true,
            trash: true
        }},
    }});
    
    map.addControl(Draw);

    // Handle drawn features (lines, shapes)
    map.on('draw.create', updateMeasurements);
    map.on('draw.update', updateMeasurements);
    map.on('draw.delete', updateMeasurements);

    function updateMeasurements(e) {{
        const data = Draw.getAll();
        let sidebarContent = "";
        if (data.features.length > 0) {{
            const features = data.features;
            features.forEach(function(feature, index) {{
                if (feature.geometry.type === 'LineString') {{
                    const length = turf.length(feature);
                    sidebarContent += `Line ${index + 1}: Length = ${length.toFixed(2)} km<br>`;
                }} else if (feature.geometry.type === 'Polygon') {{
                    const bbox = turf.bbox(feature);
                    const width = turf.distance([bbox[0], bbox[1]], [bbox[2], bbox[1]]);
                    const height = turf.distance([bbox[0], bbox[1]], [bbox[0], bbox[3]]);
                    sidebarContent += `Polygon ${index + 1}: Width = ${width.toFixed(2)} km, Height = ${height.toFixed(2)} km<br>`;
                }}
            }});
        }} else {{
            sidebarContent = "No features drawn yet.";
        }}
        window.parent.postMessage(sidebarContent, "*");
    }}
</script>
</body>
</html>
"""

# Render the Mapbox 3D Satellite map with drawing functionality and custom features
components.html(mapbox_map_html, height=600)

# Placeholder to store measurement data
if 'measurement_data' not in st.session_state:
    st.session_state['measurement_data'] = ""

# JavaScript listener to capture the messages from the map and send to Streamlit
components.html(f"""
    <script>
    window.addEventListener('message', function(event) {{
        const messageData = event.data;
        if (typeof messageData === 'string') {{
            const streamlitUpdateMessage = {{
                'type': 'update',
                'data': messageData
            }};
            window.parent.postMessage(streamlitUpdateMessage, "*");
        }}
    }});
    </script>
""", height=0)

# This part updates the session state and displays the message in the sidebar
if 'measurement_data' in st.session_state:
    measurement_display.markdown(st.session_state['measurement_data'])

# Use a custom JavaScript message handler to update session state
def message_handler():
    components.html("""
        <script>
        window.addEventListener('message', (event) => {
            const messageData = event.data;
            if (messageData && messageData.type === 'update') {
                window.parent.postMessage(messageData.data, "*");
            }
        });
        </script>
    """, height=0)

# Call the handler to listen to JavaScript messages
message_handler()
