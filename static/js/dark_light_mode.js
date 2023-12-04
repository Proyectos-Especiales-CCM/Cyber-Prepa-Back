function getCookie(name) {
     var cookieValue = null;
     if (document.cookie && document.cookie !== '') {
         var cookies = document.cookie.split(';');
         for (var i = 0; i < cookies.length; i++) {
             var cookie = cookies[i].trim();
             // Does this cookie string begin with the name we want?
             if (cookie.substring(0, name.length + 1) === (name + '=')) {
                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                 break;
             }
         }
     }
     return cookieValue;
 }
 var csrftoken = getCookie('csrftoken');

 var sassFile = "{% static 'css' %}"

function swapStyles(sheet) {
     document.getElementById('mode-stylesheet').href = sassFile + '/' + sheet
     localStorage.setItem('theme', sheet);
     updateTheme(sheet);
} 

function loadSettings(){
     var url = "{% url 'user_settings' %}"
     fetch(url, {
          method:'GET',
          headers:{
               'Content-type':'application/json'
          }
     })
     .then((response) => response.json())
     .then(function(data){

          console.log('Data:', data)

          var theme = data.value;
          
          if (theme == 'main-light.min.css' || null){
               swapStyles('main-light.min.css')
          }else if(theme == 'main.min.css'){
               swapStyles('main.min.css')
          }
     })

}

loadSettings()


function updateTheme(theme){
	var url = "{% url 'update_theme' %}"
	fetch(url, {
		method:'POST',
		headers:{
			'Content-type':'application/json',
			'X-CSRFToken':csrftoken,
		},
		body:JSON.stringify({'theme':theme})
	})
}