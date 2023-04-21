// Seleccionar el elemento select del campo "nombre_ubicacion"
var ubicacionSelect = document.querySelector("#id_nombre_ubicacion");

// Agregar un evento de cambio al select
ubicacionSelect.addEventListener("change", function() {
    // Obtener el valor seleccionado
    var nombreUbicacion = this.value;

    // Enviar una solicitud HTTP al archivo apiern.py para obtener la latitud y longitud
    // correspondientes a la ubicación elegida
    $.get("apiern.py", {nombre_ubicacion: nombreUbicacion}, function(data) {
        // Actualizar los valores de los campos de latitud y longitud en el formulario HTML
        // con los valores recibidos
        document.querySelector("#id_latitud").value = data.latitud;
        document.querySelector("#id_longitud").value = data.longitud;
    });
});

