modalSanciones.addEventListener('show.bs.modal', function (event) {
    // Button that triggered the modal
    var button = event.relatedTarget
    var recipient = button.getAttribute('data-bs-matricula')
    // If necessary, you could initiate an AJAX request here
    // and then do the updating in a callback.
    // Update the modal's content.
    var modalTitle = modalSanciones.querySelector('.modal-title')
    var modalBodyInput = modalSanciones.querySelector('.modal-body input')

    modalTitle.textContent = 'Sancion'
    modalBodyInput.value = recipient
})
