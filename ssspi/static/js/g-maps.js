let geocoder;
let map;
let marker;

function initMap() {
  let nombre_ubicacion = document.getElementById("id_nombre_ubicacion");
  let initialLat = document.getElementById("id_latitud").value;
  let initialLong = document.getElementById("id_longitud").value;
  let switch_ubicacion = document.getElementById("switch_ubicacion");
  let select_ubicacion = document.getElementById("ubicacion_predefinida");
  let input_latitud = document.getElementById("id_latitud");
  let input_longitud = document.getElementById("id_longitud");

  // Event listener de switch cambio de modo ubicacion
  switch_ubicacion.addEventListener("change", (e) => {
    let u_predef = document.getElementById("u_predef");
    let u_manual = document.getElementById("u_manual");

    if (e.target.checked == true) {
      u_predef.style.display = "block";
      u_manual.style.display = "none";
      

      
      // mover el marker a la ubicación predefinida seleccionada
      let selectedOption = select_ubicacion.options[select_ubicacion.selectedIndex];
      let latitud = selectedOption.dataset.latitud;
      let longitud = selectedOption.dataset.longitud;
      let latlng = new google.maps.LatLng(latitud, longitud);

      // Actualizar la posición del marker, el mapa y los campos de latitud y longitud
      marker.setPosition(latlng);
      map.panTo(latlng);
      input_latitud.value = latitud;
      input_longitud.value = longitud;
    } else {
      // Ingreso manual de la ubicación
      u_predef.style.display = "none";
      u_manual.style.display = "block";
    }
  });

  // Event listener para cambios en los campos de ubicación manual
  let inputs = document.querySelectorAll("#u_manual input");
  for (let i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener("change", (e) => {
      let latitud = parseFloat(input_latitud.value);
      let longitud = parseFloat(input_longitud.value);
      let latlng = new google.maps.LatLng(latitud, longitud);
      marker.setPosition(latlng);
      map.panTo(latlng);
    });
  }


  // Configuración inicial del mapa
  initialLat = initialLat ? initialLat : -33.56;
  initialLong = initialLong ? initialLong : -70.79;
  let latlng = new google.maps.LatLng(initialLat, initialLong);
  let options = {
    zoom: 9,
    center: latlng,
  };
  map = new google.maps.Map(document.getElementById("mapa"), options);

  geocoder = new google.maps.Geocoder();

  marker = new google.maps.Marker({
    map: map,
    draggable: true,
    position: latlng,
  });

  // Event listener para mover el marker manualmente
  google.maps.event.addListener(marker, "dragend", function () {
    let point = marker.getPosition();
    map.panTo(point);
    geocoder.geocode({ latLng: marker.getPosition() }, function (results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
        marker.setPosition(results[0].geometry.location);
        input_latitud.value = Number(marker.getPosition().lat().toFixed(2));
        input_longitud.value = Number(marker.getPosition().lng().toFixed(2));
      }
    });
  });
  // Event listener para cambiar la ubicación predefinida, verificar por que no funciona
  // select_ubicacion.addEventListener("change", (e) => {
  //   let selectedOption = select_ubicacion.options[select_ubicacion.selectedIndex];
  //   let latitud = parseFloat(selectedOption.dataset.latitud);
  //   let longitud = parseFloat(selectedOption.dataset.longitud);
  //   let latlng = new google.maps.LatLng(latitud, longitud);
  //   marker.setPosition(latlng);
  //   map.panTo(latlng);
  //   input_latitud.value = latitud;
  //   input_longitud.value = longitud;
  // });
}

window.initMap = initMap;
