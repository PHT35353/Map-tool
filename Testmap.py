import streamlit as st
import streamlit.components.v1 as components
import json
import requests

# Set up a title for the app
st.title("Interactive Map Tool with 3D Zoomable & Rotatable Mapbox Satellite View")

# Add instructions
st.markdown("""
This tool allows you to:
1. Select an area of the map by drawing a rectangle and customize its name.
2. Place Circle Markers (landmarks) with custom names.
3. Draw lines (pipes) between Circle Markers, and the lines will be associated with these landmarks.
4. Show the width and length of drawn rectangles and the length of drawn lines on the map and sidebar.
5. Save your drawings as a GeoJSON file and load it back.
6. Search for a location using latitude and longitude, or by entering an address.
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

# Fullscreen control added
fullscreen_control = True

# Mapbox GL JS API token
mapbox_access_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# Save and load GeoJSON functionality in the sidebar
st.sidebar.title("Save and Load Drawings")
saved_geojson = st.sidebar.file_uploader("Upload GeoJSON", type=["geojson"])

if st.sidebar.button("Save Drawings as GeoJSON"):
    st.session_state["save_geojson"] = True

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
        defaultMode: 'draw_polygon'
    }});
    
    map.addControl(Draw);

    let landmarkCount = 0;
    let landmarks = [];

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
                    
                    const popup = new mapboxgl.Popup()
                        .setLngLat(startCoord)
                        .setHTML('<p>Line belongs to: ' + (startLandmark?.properties.name || 'Unknown') + ' - ' + (endLandmark?.properties.name || 'Unknown') + '<br>Length: ' + length.toFixed(2) + ' km</p>')
                        .addTo(map);
                    
                    sidebarContent += '<p>Line ' + (index + 1) + ': ' + (startLandmark?.properties.name || 'Unknown') + ' - ' + (endLandmark?.properties.name || 'Unknown') + '<br>Length: ' + length.toFixed(2) + ' km</p>';
                }} else if (feature.geometry.type === 'Point' && !feature.properties.name) {{
                    feature.properties.name = "Landmark " + (landmarkCount + 1);
                    landmarks.push(feature);
                    sidebarContent += '<p>Landmark ' + (landmarkCount + 1) + ': ' + feature.properties.name + '</p>';
                    landmarkCount++;
                }} else if (feature.geometry.type === 'Polygon') {{
                    const bbox = turf.bbox(feature);
                    const width = turf.distance([bbox[0], bbox[1]], [bbox[2], bbox[1]]);
                    const height = turf.distance([bbox[0], bbox[1]], [bbox[0], bbox[3]]);
                    
                    const popup = new mapboxgl.Popup()
                        .setLngLat(feature.geometry.coordinates[0][0])
                        .setHTML('<p>Rectangle ' + (index + 1) + ' - Width: ' + width.toFixed(2) + ' km, Height: ' + height.toFixed(2) + ' km</p>')
                        .addTo(map);
                    
                    sidebarContent += '<p>Rectangle ' + (index + 1) + ': Width = ' + width.toFixed(2) + ' km, Height = ' + height.toFixed(2) + ' km</p>';
                }}
            }});
        }} else {{
            sidebarContent = "<p>No features drawn yet.</p>";
        }}
        window.parent.postMessage(sidebarContent, "*");
    }}

    // Send GeoJSON data to Streamlit when requested
    window.addEventListener('message', function(event) {{
        if (event.data === 'save_geojson') {{
            const geojson = Draw.getAll();
            window.parent.postMessage(JSON.stringify(geojson), "*");
        }}
    }});

    // Load GeoJSON data if uploaded
    {f"""
    const savedGeoJSON = {json.dumps(json.load(saved_geojson))};
    Draw.set(savedGeoJSON);
    """ if saved_geojson else ""}
</script>
</body>
</html>
"""

# Render the Mapbox 3D Satellite map with drawing functionality and custom features
components.html(mapbox_map_html, height=600)

# Handle saving the GeoJSON from JavaScript
if "save_geojson" in st.session_state:
    components.html(
        """
        <script>
        window.parent.postMessage("save_geojson", "*");
        </script>
        """,
        height=0
    )

# JavaScript callback function to capture the GeoJSON and trigger the download
def js_callback(data):
    geojson = json.loads(data)
    st.download_button(label="Download GeoJSON", data=json.dumps(geojson), file_name="drawings.geojson", mime="application/json")
    del st.session_state["save_geojson"]

components.html(
    """
    <script>
    window.addEventListener('message', function(event) {
        const geojsonData = event.data;
        if (geojsonData) {
            window.parent.postMessage(geojsonData, "*");
        }
    });
    </script>
    """,
    height=0
)

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
