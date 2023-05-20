// Função para inicializar o mapa
function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        center: {lat: -14.235004, lng: -51.92528},
        zoom: 4.5,
        mapTypeControl: true,
    });

    map.mapTypeControl = false;

    const locationButton = document.createElement("button");

    locationButton.textContent = "Minha Localização";
    locationButton.classList.add("custom-map-control-button");
    locationButton.addEventListener("click", () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };
                    map.zoom = 10;
                    map.setCenter(pos);
                },
                () => {
                    handleLocationError(true, infoWindow, map.getCenter());
                }
            );
        } else {
            // Browser doesn't support Geolocation
            handleLocationError(false, infoWindow, map.getCenter());
        }
    });

    function handleLocationError(browserHasGeolocation, infoWindow, pos) {
        infoWindow.setPosition(pos);
        infoWindow.setContent(
            browserHasGeolocation
                ? "Error: Falha em usar a geolocalização."
                : "Error: Por favor, atualize ou troque seu navegador para usar a geolocalização"
        );
        infoWindow.open(map);
    }


    //Dados do Heatmap
    var heatmapData = [
        //Aracaju - Sergipe
        {location: new google.maps.LatLng(-10.91, -37.07), weight: null},
        //Belém - Pará
        {location: new google.maps.LatLng(-1.46, -48.48), weight: null},
        //Belo Horizonte - Minas Gerais
        {location: new google.maps.LatLng(-19.92, -43.94), weight: null},
        //Boa Vista - Roraima
        {location: new google.maps.LatLng(2.82, -60.67), weight: null},
        //Brasília
        {location: new google.maps.LatLng(-15.78, -47.92), weight: null},
        //Campo Grande
        {location: new google.maps.LatLng(-20.481389, -54.616111), weight: null},
        //Cuiabá - Mato Grosso
        {location: new google.maps.LatLng(-15.6, -56.1), weight: null},
        //Curitiba - Paraná
        {location: new google.maps.LatLng(-25.42, -49.29), weight: null},
        //Florianópolis - Santa Catarina
        {location: new google.maps.LatLng(-27.59, -48.55), weight: null},
        //Fortaleza - Ceará
        {location: new google.maps.LatLng(-3.71, -38.54), weight: null},
        //Goiânia - Goiás
        {location: new google.maps.LatLng(-16.68, -49.25), weight: null},
        //João Pessoa - Paraíba
        {location: new google.maps.LatLng(-7.12, -34.86), weight: null},
        //Macapá - Amapá
        {location: new google.maps.LatLng(0.035, -51.07), weight: null},
        //Maceió - Alagoas
        {location: new google.maps.LatLng(-9.66, -35.73), weight: null},
        //Manaus - Amazonas
        {location: new google.maps.LatLng(-3.11, -60.02), weight: null},
        //Natal - Rio Grande do Norte
        {location: new google.maps.LatLng(-5.81, -35.21), weight: null},
        //Palmas - Tocantins
        {location: new google.maps.LatLng(-10.24, -48.35), weight: null},
        //Porto Alegre - Rio Grande do Sul
        {location: new google.maps.LatLng(-30.03, -51.23), weight: null},
        //Porto Velho - Rondônia
        {location: new google.maps.LatLng(-8.76, -63.9), weight: null},
        //Recife - Pernambuco
        {location: new google.maps.LatLng(-8.05, -34.9), weight: null},
        //Rio Branco - Acre
        {location: new google.maps.LatLng(-9.97, -67.81), weight: null},
        //Rio de Janeiro
        {location: new google.maps.LatLng(-22.91, -43.2), weight: null},
        //Salvador - Bahia
        {location: new google.maps.LatLng(-12.97, -38.51), weight: null},
        //São Luís - Maranhão
        {location: new google.maps.LatLng(-2.53, -44.3), weight: null},
        //São Paulo
        {location: new google.maps.LatLng(-23.55, -46.64), weight: null},
        //Teresina - Piauí
        {location: new google.maps.LatLng(-5.09, -42.8), weight: null},
        //Vitória - Espírito Santo
        {location: new google.maps.LatLng(-20.32, -40.34), weight: null},
    ];

    // Configurações do heatmap
    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        map: map,
        radius: 20,
        gradient: [
            "rgba(0,0,0,0.5)",
            "rgb(0,0,255)",
            "rgb(255,98,0)",
            "rgb(255,255,0)",
        ],
    });

    // Definir limite de cores para o heatmap
    heatmap.setOptions({
        dissipating: true,
        maxIntensity: 100,
        radius: 50,
    });

    //Card de pesquisa de cidades
    const card = document.getElementById("pac-card");
    const input = document.getElementById("pac-input");
    const options = {
        fields: ["formatted_address", "geometry", "name"],
        strictBounds: false,
        types: ["establishment"],
    };

    map.controls[google.maps.ControlPosition.LEFT_TOP].push(card);
    map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(locationButton);

    const autocomplete = new google.maps.places.Autocomplete(input);

    autocomplete.bindTo("bounds", map);
    autocomplete.setTypes(["(cities)"]);

    const marker = new google.maps.Marker({
        map,
        anchorPoint: new google.maps.Point(0, -29),
    });

    autocomplete.addListener("place_changed", () => {
        marker.setVisible(true);

        const place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
            window.alert("O nome digitado não pôde ser encontrado: '" + place.name + "'");
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(10);
        }

        marker.setPosition(place.geometry.location);
        marker.setVisible(true);
        infowindowContent.children["place-name"].textContent = place.name;
        infowindowContent.children["place-address"].textContent =
            place.formatted_address;
        infowindow.open(map, marker);
    });


}

window.initMap = initMap;


