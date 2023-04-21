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









/* Select Anidados*/

/*sector.addEventListener('change', selectsector);


function selectsector(e) {
  //console.log(e.target);
  let aplicaciones = [[], alimentos, quimica];
  let alimentos = new Array('Seleccione Aplicación','Alcoholes y destilados','Alimentación animal', 'Panadería', 'Cerveza', 'Enlatados y jugos', 'Cocoa, chocolates y dulces', 'Café y té', 'Productos Lácteos', 'Acéites y grasas', 'Pescado', 'Carne', 'Bebidas no alcohólicas', 'Preparados', 'Pastas', 'Azucar', 'Vino', 'Otros productos');
  let quimica = new Array('Seleccione Aplicación','Productos agroquímicos','Cosméticos y detergentes', 'Productos químicos básicos', 'Pinturas y barnices', 'Otros');
  console.log(e.target.value);
  if (sector.value == 'Alimento' ){
    alimentos.forEach(i => {
      document.getElementById("id_aplicacion").innerHTML += "<option value='" +i.nombre+"'> "+i.nombre+ "</option>";
      console.log(i.nombre)});
          {   
          }
  }
  console.log(sector);
  if (sector != '0') {
    let mi_sector = aplicaciones[sector];
    let num_aplicaciones = aplicaciones[sector].length; 
    document.simform.sector.length = num_aplicaciones;

    for (let i = 0; i < num_sectores; i++) {
      document.simform.sector.options[i].value=aplicaciones[i];
      document.simform.sector.options[i].text=aplicacione[i]; 
    }

  }
  else {
    document.simform.sector.options[0].value ="";
    document.simform.sector.options[0].text ="";
  }
  document.simform.sector.opttion[0].selected = true;

}*/

 






//console.log(sup_coletores);


/* */

// function showSelected(){

//   if (document.getElementById('label_sector').value != "" ){
//     const label_sector = document.getElementById('label_sector');
//     const label_aplicacion = document.getElementById('label_aplicacion');
//     label_sector.classList.add("active");
//     label_aplicacion.classList.add("active");
//   }
//   else{
//   if (document.getElementById('label_sector').value != "" ){
//     const label_sector = document.getElementById('label_sector');
//     const label_aplicacion = document.getElementById('label_aplicacion');
//     label_sector.classList.remove("active");
//     label_aplicacion.classList.remove("active");
//     }
//    }
// }

