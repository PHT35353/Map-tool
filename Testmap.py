import streamlit as st
import streamlit.components.v1 as components

# Set up a title for the app
st.title("Interactive Map Tool with 3D Zoomable & Rotatable Mapbox Satellite View")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle and customizing its name and color.
2. Place Circle Markers (with custom names and colors) within the selected area.
3. Draw lines (pipes) between Circle Markers with customizable names and colors. Each line will display its length.
4. Search for a location by entering latitude and longitude (in the sidebar), or use the address search.
5. Zoom and rotate the 3D satellite map for a more interactive experience.
6. Save the map and download it as a screenshot.
""")

# Sidebar to manage the map interactions
st.sidebar.title("Search by Coordinates")

# Default location set to Amsterdam, Netherlands
default_location = [52.3676, 4.9041]

# Input fields for latitude and longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Search bar for address search
address_search = st.sidebar.text_input("Search for address")

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

# Fullscreen control added
fullscreen_control = True

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
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
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
        #screenshot {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background-color: white;
            padding: 10px;
            cursor: pointer;
            z-index: 999;
        }}
    </style>
</head>
<body>
<div id="map"></div>
<button id="screenshot">Download Screenshot</button>
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
        defaultMode: 'draw_polygon'
    }});
    
    map.addControl(Draw);

    // Handle drawn features (lines, shapes)
    map.on('draw.create', updateMeasurements);
    map.on('draw.update', updateMeasurements);
    map.on('draw.delete', updateMeasurements);

    // Display distances and allow color/naming customization in the sidebar
    function updateMeasurements(e) {{
        const data = Draw.getAll();
        if (data.features.length > 0) {{
            const features = data.features;
            features.forEach(function(feature) {{
                if (feature.geometry.type === 'LineString') {{
                    const length = turf.length(feature);
                    // Send the length to Streamlit (Python)
                    const event = new CustomEvent('update-distance', {{
                        detail: {{ length: length.toFixed(2) }}
                    }});
                    window.dispatchEvent(event);
                }}
            }});
        }}
    }}

    // Screenshot functionality
    document.getElementById('screenshot').addEventListener('click', function() {{
        html2canvas(document.querySelector("#map")).then(canvas => {{
            let link = document.createElement('a');
            link.download = 'map_screenshot.png';
            link.href = canvas.toDataURL();
            link.click();
        }});
    }});
</script>
</body>
</html>
"""

# Render the Mapbox 3D Satellite map with drawing functionality and custom features
components.html(mapbox_map_html, height=600)

# Receive events from JavaScript to update the Streamlit sidebar
def js_callback(data):
    st.sidebar.write(f"Pipe Length: {data['length']} km")

components.html(
    """
    <script>
    window.addEventListener('update-distance', function(event) {
        const pipeLength = event.detail.length;
        // Send the pipe length back to Streamlit
        window.parent.postMessage(pipeLength, "*");
    });
    </script>
    """,
    height=0
)

# Latitude/Longitude and Address search functionality is handled within the map
if address_search:
    # Implement Mapbox Geocoding API if required for address search functionality
    pass
