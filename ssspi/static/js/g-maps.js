/*Google Maps API */

// Inputs Ubicacion



let geocoder;
let map;
let marker;


// Consumo API Googlemaps
 
function initMap() {

    let nombre_ubicacion = document.getElementById('id_nombre_ubicacion');
    let initialLat = document.getElementById("id_latitud").value;
    let initialLong = document.getElementById("id_longitud").value;

     // Event listener de switch cambio de modo ubicacion

     switch_ubicacion.addEventListener('change', (e)=> {
        let u_predef = document.getElementById("u_predef");
        let u_manual = document.getElementById("u_manual");
        //let nombre_ubicacion = document.getElementById("id_nombre_ubicacion");
        
        if (e.target.checked == true) {
            //Ubicación predeterminada

            u_predef.style.display = "block";
            u_manual.style.display = "none";
            
        }
        else {
            //Ingreso manual de la ubicación

            u_predef.style.display = "none";
            u_manual.style.display = "block";
        }

    });


    // Event listener del Contenedor ubicación
    cont_ubica.addEventListener('change', (e)=> {
        //console.log(e.target.tagName);
        //console.log(e.target.value);
        if (e.target && e.target.tagName === 'INPUT'){
            if (e.target.id == 'id_nombre_ubicacion'){
                if(e.target.id == 'Santiago'){
                    console.log('Santiago');
                    
                    return (latitud_res.value = initialLat = -33.45, initialLong =-70.67);
                }
                if(e.target.id == 'La Cisterna'){
                    latitud_res.value = e.target.value;
                    console.log('La Cisterna');
                    return (initialLat = -33.55, initialLong =-70.68);
                }

                return (ubicacion_res.value = e.target.value);
            }
            if (e.target.id == 'id_latitud'){
                console.log(e.target.value);
                
                return ((latitud_res.value = e.target.value), initialLat = e.target.value);
            }
            if (e.target.id == 'id_longitud'){
                console.log(e.target.value);
                
                return ((longitud_res.value = e.target.value), initialLong = e.target.value);
            }            
        }
        else {
            //
            
        }
    });



    initialLat = initialLat?initialLat:-33.56;
    initialLong = initialLong?initialLong:-70.79;

    let latlng = new google.maps.LatLng(initialLat, initialLong);
    
    //let myLatLng = { lat: -33.56, lng: -70.79 };

   


   
    
    //console.log(myLatLng);
    /*let map = new google.maps.Map(document.getElementById("mapa"), {
        //center: myLatLng,
        center: latlng,
        zoom: 9,
    });
    marker = new google.maps.Marker({
        map: map,
        draggable: true,
        position: map.getCenter(),
        title: "Google Maps API",
    });

    // Configuración de cursor y funcionamiento
    marker.addListener('dragend', function(e) {
        let latitud = document.getElementById('id_latitud').value = Number((this.getPosition().lat()).toFixed(2));
        if (latitud != 0){
            const lati = document.getElementById('label-lat');
            lati.classList.add("active");
        }
        let longitud = document.getElementById('id_longitud').value = Number((this.getPosition().lng()).toFixed(2));
        if (longitud != 0){
            const longi = document.getElementById('label-long');
            longi.classList.add("active");
        }

    });*/

     // Google Maps API

    let options = {
        zoom: 9,
        center: latlng,
    };

    map = new google.maps.Map(document.getElementById("mapa"), options);

    geocoder = new google.maps.Geocoder();

    marker = new google.maps.Marker({
        map: map,
        draggable: true,
        position: latlng
    });

    google.maps.event.addListener(marker, "dragend", function () {
        let point = marker.getPosition();
        map.panTo(point);
        geocoder.geocode({'latLng': marker.getPosition()}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                map.setCenter(results[0].geometry.location);
                marker.setPosition(results[0].geometry.location);
                //document.getElementById("id_nombre_ubicacion").value.results[1].formatted_address;
                document.getElementById('id_latitud').value = Number((marker.getPosition().lat()).toFixed(2));
                //document.getElementById("id_latitud").value.marker.getPosition().lat();
                //document.getElementById("id_longitud").value.marker.getPosition().lng();
                let longitud = document.getElementById('id_longitud').value = Number((marker.getPosition().lng()).toFixed(2));
            }
        });
    });

    
}
 
window.initMap = initMap;

///


/*

function initialize() {
    let initialLat = document.getElementById("id_latitud").value;
    let initialLng = document.getElementById("id_longitud").value;

    initialLat = initialLat?initialLat:-33.56;
    initialLong = initialLong?initialLong:-70.79;

    let latlng = new google.maps.LatLng(initialLat, initialLong);
    let options = {
        zoom: 16,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById("geomap"), options);

    geocoder = new google.maps.Geocoder();

    marker = new google.maps.Marker({
        map: map,
        draggable: true,
        position: latlng
    });

    google.maps.event.addListener(marker, "dragend", function () {
        let point = marker.getPosition();
        map.panTo(point);
        geocoder.geocode({'latLng': marker.getPosition()}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                map.setCenter(results[0].geometry.location);
                marker.setPosition(results[0].geometry.location);
                document.getElementByClassName("search_addr").val(results[0].formatted_address);
                document.getElementByClassName("search_latitude").val(marker.getPosition().lat());
                document.getElementByClassName("search_longitude").val(marker.getPosition().lng());
            }
        });
    });

}

document.ready(function () {
    
    initialize();
    
    
    let PostCodeid = '#search_location';
    document.addEventListener("DOMContentLoaded", () => {
        PostCodeid.autocomplete({
            source: function (request, response) {
                geocoder.geocode({
                    'address': request.term
                }, function (results, status) {
                    response($.map(results, function (item) {
                        return {
                            label: item.formatted_address,
                            value: item.formatted_address,
                            lat: item.geometry.location.lat(),
                            lon: item.geometry.location.lng()
                        };
                    }));
                });
            },
            select: function (event, ui) {
                document.getElementByClassName("search_addr").val(ui.item.value);
                document.getElementByClassName("search_latitude").val(ui.item.lat);
                document.getElementByClassName("search_longitude").val(ui.item.lon);
                let latlng = new google.maps.LatLng(ui.item.lat, ui.item.lon);
                marker.setPosition(latlng);
                initialize();
            }
        });
    });
    
    
    document.getElementByClassName("get_map").click(function (e) {
        let address = PostCodeid.value;
        geocoder.geocode({'address': address}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                map.setCenter(results[0].geometry.location);
                marker.setPosition(results[0].geometry.location);
                document.getElementByClassName("search_addr").val(results[0].formatted_address);
                document.getElementByClassName("search_latitude").val(marker.getPosition().lat());
                document.getElementByClassName("search_longitude").val(marker.getPosition().lng());
            } else {
                alert("Geocode was not successful for the following reason: " + status);
            }
        });
        e.preventDefault();
    });

    
    google.maps.event.addListener(marker, 'drag', function () {
        geocoder.geocode({'latLng': marker.getPosition()}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                if (results[0]) {
                    document.getElementByClassName("search_addr").val(results[0].formatted_address);
                    document.getElementByClassName("search_latitude").val(marker.getPosition().lat());
                    document.getElementByClassName("search_longitude").val(marker.getPosition().lng());
                }
            }
        });
    });
});*/
