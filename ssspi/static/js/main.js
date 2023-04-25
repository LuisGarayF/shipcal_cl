document.addEventListener('DOMContentLoaded', function() {
  
  // /* Tooltip*/
  var elems = document.querySelectorAll('.tooltipped');
  var instances = M.Tooltip.init(elems);
});





/* Búsqueda en tabla */

function getTabla() {
  // Declare variables
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("buscar");
  filter = input.value.toUpperCase();
  table = document.getElementById("datatable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

            
/* Eventos */

// ubicacion.addEventListener('change', (e)=> {
//   ubicacion_res.innerText = e.target.value;
// });
// latitud.addEventListener('change', (e)=> {
//   latitud_res.innerHTML = e.target.value;
//   console.log(e.target.value);
// });
// longitud.addEventListener('change', (e)=> {
//    longitud_res.innerHTML = e.target.value;
//    console.log(e.target.value);
// });
combustible.addEventListener('change', (e)=> {
  combustible_res.innerText = e.target.value;
});
demanda_anual.addEventListener('change', (e)=> {
  demanda_anual_res.innerText = e.target.value;
});
unidad_demanda.addEventListener('change', (e)=> {
  console.log(e.target.value);
  unidad_demanda_res.innerText = e.target.value;

});
ini_jornada.addEventListener('change', (e)=> {
  ini_jornada_res.innerHTML = e.target.value;
});
term_jornada.addEventListener('change', (e)=> {
  term_jornada_res.innerHTML = e.target.value;
});

// demanda_enero.addEventListener('change', (e)=> {
//   demanda_enero_res.textContent = e.target.value;
// });

// demanda_febrero.addEventListener('change', (e)=> {
//   demanda_febrero_res.textContent = e.target.value;
// });

// demanda_marzo.addEventListener('change', (e)=> {
//   demanda_marzo_res.textContent = e.target.value;
// });





