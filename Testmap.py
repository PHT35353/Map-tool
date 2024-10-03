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

# Mapbox GL JS API token
mapbox_access_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# Placeholder for the sidebar content that will display distances and dimensions
sidebar_placeholder = st.sidebar.empty()

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

    let landmarkCount = 0;
    let landmarks = [];

    // Store names and colors of polygons, lines, and markers once during creation
    let featureColors = {{}};
    let featureNames = {{}};

    // Handle drawn features (lines, shapes)
    map.on('draw.create', updateMeasurements);
    map.on('draw.update', updateMeasurements);
    map.on('draw.delete', deleteFeature);

    function updateMeasurements(e) {{
        const data = Draw.getAll();
        let sidebarContent = "";
        if (data.features.length > 0) {{
            const features = data.features;
            features.forEach(function(feature, index) {{
                if (feature.geometry.type === 'LineString') {{
                    const length = turf.length(feature);
                    const startCoord = feature.geometry.coordinates[0];
                    const endCoord = feature.geometry.coordinates[feature.geometry.coordinates.length - 1];

                    // Identify landmarks for the start and end points of the line
                    let startLandmark = landmarks.find(lm => turf.distance(lm.geometry.coordinates, startCoord) < 0.01);
                    let endLandmark = landmarks.find(lm => turf.distance(lm.geometry.coordinates, endCoord) < 0.01);

                    // Only ask for name once
                    if (!featureNames[feature.id]) {{
                        const name = prompt("Enter a name for this line:");
                        featureNames[feature.id] = name || "Line " + (index + 1);
                    }}

                    // Assign color if not already assigned
                    if (!featureColors[feature.id]) {{
                        const lineColor = prompt("Enter a color for this line (e.g., red, purple, cyan, pink):");
                        featureColors[feature.id] = lineColor || 'blue';
                    }}

                    // Set the line's color
                    map.addLayer({{
                        id: 'line-' + feature.id,
                        type: 'line',
                        source: {{
                            type: 'geojson',
                            data: feature
                        }},
                        layout: {{}},
                        paint: {{
                            'line-color': featureColors[feature.id],
                            'line-width': 4
                        }}
                    }});

                    sidebarContent += '<p>Line ' + featureNames[feature.id] + ': Length = ' + length.toFixed(2) + ' km</p>';
                }} else if (feature.geometry.type === 'Point') {{
                    if (!feature.properties.name) {{
                        if (!featureNames[feature.id]) {{
                            const name = prompt("Enter a name for this landmark:");
                            feature.properties.name = name || "Landmark " + (landmarkCount + 1);
                            featureNames[feature.id] = feature.properties.name;
                            landmarks.push(feature);
                            landmarkCount++;
                        }} else {{
                            feature.properties.name = featureNames[feature.id];
                        }}
                    }}

                    sidebarContent += '<p>Landmark ' + feature.properties.name + '</p>';
                }} else if (feature.geometry.type === 'Polygon') {{
                    if (!feature.properties.name) {{
                        if (!featureNames[feature.id]) {{
                            const name = prompt("Enter a name for this polygon:");
                            feature.properties.name = name || "Polygon " + (index + 1);
                            featureNames[feature.id] = feature.properties.name;
                        }} else {{
                            feature.properties.name = featureNames[feature.id];
                        }}
                    }}

                    const bbox = turf.bbox(feature);
                    const width = turf.distance([bbox[0], bbox[1]], [bbox[2], bbox[1]]);
                    const height = turf.distance([bbox[0], bbox[1]], [bbox[0], bbox[3]]);
                    
                    sidebarContent += '<p>Polygon ' + feature.properties.name + ': Width = ' + width.toFixed(2) + ' km, Height = ' + height.toFixed(2) + ' km</p>';
                }}
            }});
        }} else {{
            sidebarContent = "<p>No features drawn yet.</p>";
        }}
        window.parent.postMessage(sidebarContent, "*");
    }}

    // Function to handle deletion of features
    function deleteFeature(e) {{
        const features = e.features;
        features.forEach(function(feature) {{
            // Remove feature colors and names on deletion
            delete featureColors[feature.id];
            delete featureNames[feature.id];

            // Remove the layer corresponding to the deleted feature
            map.removeLayer('line-' + feature.id);
            map.removeLayer('polygon-' + feature.id);
            map.removeLayer('marker-' + feature.id);
        }});
        updateMeasurements();
    }}
</script>
</body>
</html>
"""

# Render the Mapbox 3D Satellite map with drawing functionality and custom features
components.html(mapbox_map_html, height=600)

# Address search using Mapbox Geocoding API
if address_search:
    geocode_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address_search}.json?access_token={mapbox_access_token}"
    # Request the geocoded location
    try:
        response = requests.get(geocode_url)
        if response.status_code == 200:
            geo_data = response.json()
            if len(geo_data['features']) > 0:
                coordinates = geo_data['features'][0]['center']
                latitude, longitude = coordinates[1], coordinates[0]
                st.sidebar.success(f"Address found: {geo_data['features'][0]['place_name']}")
                st.sidebar.write(f"Coordinates: Latitude {latitude}, Longitude {longitude}")
            else:
                st.sidebar.error("Address not found.")
        else:
            st.sidebar.error("Error connecting to the Mapbox API.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# This will receive the measurements from the JavaScript code and display it in the sidebar
components.iframe("about:blank", height=0)  # Invisible iframe to receive sidebar content

st.sidebar.text("Feature Measurements:")

# Capture the measurement data posted from the JavaScript in the map component
data_received = st.experimental_js_receive("message")
if data_received:
    sidebar_placeholder.markdown(data_received)  # Display the content from the JS map
