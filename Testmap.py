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
4. Search for a location by entering latitude and longitude (in the sidebar).
5. Zoom and rotate the 3D satellite map for a more interactive experience.
""")

# Sidebar to manage the map interactions
st.sidebar.title("Search by Coordinates")

# Default location set to Amsterdam, Netherlands
default_location = [52.3676, 4.9041]

# Input fields for latitude and longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

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

    // Add map controls for zoom, rotation
    map.addControl(new mapboxgl.NavigationControl());

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

    function updateMeasurements(e) {{
        const data = Draw.getAll();
        if (data.features.length > 0) {{
            const features = data.features;
            features.forEach(function(feature) {{
                if (feature.geometry.type === 'LineString') {{
                    const length = turf.length(feature);
                    const popup = new mapboxgl.Popup()
                        .setLngLat(feature.geometry.coordinates[0])
                        .setHTML('<p>Line length: ' + length.toFixed(2) + ' km</p>')
                        .addTo(map);
                }}
            }});
        }}
    }}
</script>
</body>
</html>
"""

# Render the Mapbox 3D Satellite map with drawing functionality
components.html(mapbox_map_html, height=600)
