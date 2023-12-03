// function getCookie(name) {
//     var cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         var cookies = document.cookie.split(';');
//         for (var i = 0; i < cookies.length; i++) {
//             var cookie = cookies[i].trim();
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
// var csrftoken = getCookie('csrftoken');

// var cssFile = "{% static 'css' %}"

// function swapStyles(){
     // if (document.body.classList.contains('dark-mode')) {
     //      document.body.classList.remove('dark-mode');
     //      document.body.classList.add('light-mode');
     // } else if (document.body.classList.contains('light-mode')) {
     //      document.body.classList.remove('light-mode');
     //      document.body.classList.add('dark-mode');
     
     // }
     // document.body.classList.toggle('dark-mode');
     // document.body.classList.toggle('light-mode');

     // Save the current mode preference in localStorage
     // const currentMode = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
     // localStorage.setItem('theme', currentMode);

     // document.getElementById('mystylesheet').href = cssFile + '/' + sheet
     // localStorage.setItem('theme', sheet)

     // updateTheme(sheet)
// }

function swapStyles() {
     document.body.classList.toggle('dark-light-mode');
     const currentMode = document.body.classList.contains('dark-light-mode') ? 'light' : 'dark';
     localStorage.setItem('theme', currentMode);
 }
 

function loadInitialTheme() {

     const savedTheme = localStorage.getItem('theme');
     
     if (savedTheme === 'light') {
         document.body.classList.add('dark-light-mode');
     }
     
}
 
 loadInitialTheme();

// function loadSettings(){
//      //Call data and set local storage

//      var url = "{% url 'user_settings' %}"
//      fetch(url, {
//           method:'GET',
//           headers:{
//                'Content-type':'application/json'
//           }
//      })
//      .then((response) => response.json())
//      .then(function(data){

//           console.log('Data:', data)

//           var theme = data.value;
          
//           if (theme == 'light.css' || null){
//                swapStyles('light.css')
//           }else if(theme == 'dark.css'){
//                swapStyles('dark.css')
//           }
          

//      })

// }

// loadSettings()

// function updateTheme(theme){
//      var url = "{% url 'update_theme' %}"
//      fetch(url, {
//           method:'POST',
//           headers:{
//                'Content-type':'application/json',
//                'X-CSRFToken':csrftoken,
//           },
//           body:JSON.stringify({'theme':theme})
//      })
// }
