const draggables = document.querySelectorAll('.draggable');
const containers = document.querySelectorAll('.container-dropzone');
const cardContainers = document.querySelectorAll('.cyber__card__inner');
const modal = document.getElementById('changeUserPlayModal');
const closeBtn = document.getElementsByClassName('close')[0];
const confirmBtn = document.getElementsByClassName('confirm')[0];
const rejectBtn = document.getElementsByClassName('reject')[0];

draggables.forEach(draggable => {
	draggable.addEventListener('dragstart', () => {
		draggable.classList.add('dragging')
	});
	draggable.addEventListener('dragend', () => {
		draggable.classList.remove('dragging')
	})
})

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
		// const closestContainer = e.target.closest('[data-gameName]');
		// if (closestContainer) {
		// 	const gameName = closestContainer.getAttribute('data-gameName');
		
			$('#changeUserPlayModal').find('#id_usuario').attr('placeholder', draggable.id);
			$('#changeUserPlayModal').find('#actual_play').attr('placeholder', draggable.dataset.gameName);
			$('#changeUserPlayModal').find('#nuevo_play').attr('placeholder', cardContainer.id);
			// $('#changeUserPlayModal').find('#nuevo_play').attr('placeholder', closestContainer.id);
			$('#changeUserPlayModal').modal('show');

          	cardContainer.style.backgroundColor = ''
		}
	})
// })

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