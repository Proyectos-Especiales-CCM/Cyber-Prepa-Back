const draggables = document.querySelectorAll('.draggable');
const containers = document.querySelectorAll('.container-dropzone');
const cardContainers = document.querySelectorAll('.cyber__card__inner');
const modal = document.getElementById('confirmation_modal');
const closeBtn = document.getElementsByClassName('close')[0];
const confirmBtn = document.getElementsByClassName('confirm')[0];
const rejectBtn = document.getElementsByClassName('reject')[0];

draggables.forEach(draggable => {
	draggable.addEventListener('dragstart', () => {
		draggable.classList.add('dragging')
		// draggable.dataTransfer.setData('text/plain', draggable.id)
		// e.dataTransfer.setData('text/plain', draggable.target.id)
	});
	draggable.addEventListener('dragend', () => {
		draggable.classList.remove('dragging')
	})
})

function fire_up_modal() {
     modal.style.display = 'flex';
     document.body.style.overflow = 'hidden';

     return new Promise(resolve => {
          // $('#confirmation_modal').modal('show')
          
          $('.confirmation-button').click(function() {
               modal.style.display = 'none';
               document.body.style.overflow = 'auto';
               resolve(true)
          })

          $('.reject-button').click(function() {
               modal.style.display = 'none';
               document.body.style.overflow = 'auto';
               resolve(false)
          })
     })
}

window.onclick = function(event) {
     if (event.target == modal) {
         modal.style.display = 'none';
         document.body.style.overflow = 'auto';
     }
 }

cardContainers.forEach(cardContainer => {
     const cardContainerSibling = cardContainer.nextElementSibling
     const collapsedStudents = cardContainerSibling.querySelector('.container-dropzone')

	cardContainer.addEventListener('dragover', e => {
		e.preventDefault()
		const draggable = document.querySelector('.dragging')
		if (draggable) {
               cardContainer.style.backgroundColor = '#007bff'
          }
	})

	cardContainer.addEventListener('dragleave', () => {
		cardContainer.style.backgroundColor = ''
	})

	cardContainer.addEventListener('drop', e => {
		e.preventDefault()
          const draggable = document.querySelector('.dragging')
          if (collapsedStudents) {
               fire_up_modal().then(answerConfirmation => {
                    // closeBtn.onclick = function() {
                    //      modal.style.display = 'none';
                    //      document.body.style.overflow = 'auto';
                    //      cardContainer.style.backgroundColor = ''
                    // }
                    if (answerConfirmation) {
                         collapsedStudents.appendChild(draggable);
                         // TODO: Call the backend function here or trigger any other action based on user confirmation
                    }
               })
          }
	})

})

containers.forEach(container => {
	container.addEventListener('dragover', e => {
		e.preventDefault()
		const afterElement = getDragAfterElement(container, e.clientY)
		const draggable = document.querySelector('.dragging')
		if (afterElement == null) {
			container.appendChild(draggable)
		} else {
			container.insertBefore(draggable, afterElement)
		}
	})
})

function getDragAfterElement(container, y) {
	const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')]

	return draggableElements.reduce((closest, child) => {
		const box = child.getBoundingClientRect()
		const offset = y - box.top - box.height / 2
		if (offset < 0 && offset > closest.offset) {
			return { offset: offset, element: child }
		} else {
			return closest
		}
	}, { offset: Number.NEGATIVE_INFINITY }).element
}