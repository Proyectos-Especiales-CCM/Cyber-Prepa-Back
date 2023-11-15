document.getElementById("sancionarBtn").addEventListener("click", function() {
  var student_id = document.getElementById("matriculaSancion").value;
  var cause = document.getElementById("causaSancion").value;
  var days = document.getElementById("diasSancion").value;

  var data = {
    student_id: student_id,
    cause: cause,
    days: days
  };

  var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

  fetch('api/add-student-to-sanctioned', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(data)
  })
  .then(response => {
    if (response.ok) {
      var modal = new bootstrap.Modal(document.getElementById("modalSanciones"));
      modal.hide();
    } else {
      console.error('Error:', response);
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
});
