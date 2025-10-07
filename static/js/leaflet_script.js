document.addEventListener('DOMContentLoaded', function () {


    var map = L.map('map').setView([0, 0], 13);

    // Add a tile layer from the providers plugin
    
    var layers = {
        "CartoDB Positron": L.tileLayer.provider('CartoDB.Positron'),
        "OpenStreetMap": L.tileLayer.provider('OpenStreetMap.Mapnik')
    };
    
    // Add default layer to map first
    layers["OpenStreetMap"].addTo(map);

    // Add layer control
    L.control.layers(layers).addTo(map);

    // Load GeoJSON file
    var mapContainer = document.getElementById("map");
    var geojsonFile = mapContainer.dataset.geojson;

    fetch(`/static/geo_json/${geojsonFile}`)
        .then(response => response.json())
        .then(data => {
            // Add the GeoJSON layer to the map
            var routeLayer = L.geoJSON(data, {
                style: {
                    color: 'blue',      
                    weight: 2.45,        
                    opacity: 0.7
                }
            }).addTo(map);

            // Zoom map to the route
            map.fitBounds(routeLayer.getBounds());


            // Add start and finish markers
            var start = data.geometry.coordinates[0];  // first coordinate
            var finish = data.geometry.coordinates[data.geometry.coordinates.length - 1]; // last coordinate

            L.circleMarker([start[1], start[0]], {
                radius: 5,
                color: 'green',
                fillColor: 'lime',
                fillOpacity: 1
            }).addTo(map).bindPopup("Start");

            L.circleMarker([finish[1], finish[0]], {
                radius: 5,
                color: 'red',
                fillColor: 'orange',
                fillOpacity: 1
            }).addTo(map).bindPopup("Finish");
        })
        .catch(err => console.error("Error loading GeoJSON:", err));
});




