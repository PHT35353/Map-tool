import streamlit as st
import streamlit.components.v1 as components
import requests

# Set up a title for the app
st.title("Interactive Map Tool with Individual Colors for Features")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle and customize its name and color.
2. Place Circle Markers (landmarks) with custom names and colors.
3. Draw lines (pipes) between Circle Markers, customize their colors and names, and the lines will be associated with these landmarks.
4. Show the width and length of drawn rectangles and the length of drawn lines on the map and sidebar.
5. Search for a location using latitude and longitude, or by entering an address.
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
    map.on('draw.delete', updateMeasurements);

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

                    let startLandmark = landmarks.find(lm => turf.distance(lm.geometry.coordinates, startCoord) < 0.01);
                    let endLandmark = landmarks.find(lm => turf.distance(lm.geometry.coordinates, endCoord) < 0.01);

                    // Assign color if not already assigned
                    if (!featureColors[feature.id]) {{
                        const lineColor = prompt("Enter a color for this line (e.g., red, purple, cyan, pink):");
                        featureColors[feature.id] = lineColor || 'blue';
                    }}

                    map.setPaintProperty(
                        "custom-line-" + feature.id,
                        'line-color',
                        featureColors[feature.id]
                    );
                    
                    const popup = new mapboxgl.Popup()
                        .setLngLat(startCoord)
                        .setHTML('<p>Line belongs to: ' + (startLandmark?.properties.name || 'Unknown') + ' - ' + (endLandmark?.properties.name || 'Unknown') + '<br>Length: ' + length.toFixed(2) + ' km</p>')
                        .addTo(map);
                    
                    sidebarContent += '<p>Line ' + (index + 1) + ': ' + (startLandmark?.properties.name || 'Unknown') + ' - ' + (endLandmark?.properties.name || 'Unknown') + '<br>Length: ' + length.toFixed(2) + ' km</p>';
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

                    // Assign color if not already assigned
                    if (!featureColors[feature.id]) {{
                        const markerColor = prompt("Enter a color for this landmark (e.g., black, white):");
                        featureColors[feature.id] = markerColor || 'black';
                    }}

                    map.setPaintProperty(
                        "custom-marker-" + feature.id,
                        'circle-color',
                        featureColors[feature.id]
                    );

                    sidebarContent += '<p>' + feature.properties.name + '</p>';
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

                    // Assign color if not already assigned
                    if (!featureColors[feature.id]) {{
                        const polygonColor = prompt("Enter a color for this polygon (e.g., green, yellow):");
                        featureColors[feature.id] = polygonColor || 'yellow';
                    }}

                    map.setPaintProperty(
                        "custom-polygon-" + feature.id,
                        'fill-color',
                        featureColors[feature.id]
                    );

                    const bbox = turf.bbox(feature);
                    const width = turf.distance([bbox[0], bbox[1]], [bbox[2], bbox[1]]);
                    const height = turf.distance([bbox[0], bbox[1]], [bbox[0], bbox[3]]);
                    
                    const popup = new mapboxgl.Popup()
                        .setLngLat(feature.geometry.coordinates[0][0])
                        .setHTML('<p>' + feature.properties.name + ' - Width: ' + width.toFixed(2) + ' km, Height: ' + height.toFixed(2) + ' km</p>')
                        .addTo(map);
                    
                    sidebarContent += '<p>' + feature.properties.name + ': Width = ' + width.toFixed(2) + ' km, Height = ' + height.toFixed(2) + ' km</p>';
                }}
            }});
        }} else {{
            sidebarContent = "<p>No features drawn yet.</p>";
        }}
        window.parent.postMessage(sidebarContent, "*");
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
