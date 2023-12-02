const regulations = document.getElementsByClassName("paragraph-text");

function search() {
     let busqueda = document.getElementById("busqueda").value;
     const special = /[\\[{().+*?|^$]/g;

     if (busqueda !== "") {
          if (special.test(busqueda)) busqueda = busqueda.replace(special, "\\$&");

          let regExp = new RegExp(busqueda, "gi");

          for (let i = 0; i < regulations.length; i++) {
               regulations[i].innerHTML = (regulations[i].textContent).replace(regExp, "<mark>$&</mark>");
          }
     }
}

// function search() {
//   let busqueda = document.getElementById("busqueda").value;
//   const special = /[\\[{().+*?|^$]/g;

//   if (busqueda !== "") {
//     if (special.test(busqueda)) busqueda = busqueda.replace(special, "\\$&");

//     let regExp = new RegExp(busqueda, "gi");
//     console.log(regExp)

//     for (let i = 0; i < regulations.length; i++) {
//       const textContent = regulations[i].textContent;
//       const match = textContent.match(regExp);
//       if (match) {
//           console.log(match.index)
//       }
//     }

//       if (match) {
//         const start = match.index;
//         const end = start + match[0].length;

//         const range = document.createRange();
//         range.setStart(regulations[i].childNodes[0], start);
//         range.setEnd(regulations[i].childNodes[0], end);

//         const rect = range.getBoundingClientRect();

//         window.scrollTo({
//           top: rect.top + window.scrollY,
//           behavior: "smooth",
//         });

//         regulations[i].innerHTML = textContent.substring(0, start) + "<mark>" + textContent.substring(start, end) + "</mark>" + textContent.substring(end);
//         break;
//       }
//     }
//   }
// }
