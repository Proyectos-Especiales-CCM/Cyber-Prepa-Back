/* Required variables for AJAX requests */
// CSRF token
const CSRFTOKEN = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Get current IP for AJAX requests
let currentIP = window.location.hostname;
if (currentIP === "127.0.0.1" || currentIP === "localhost") {
    currentIP = currentIP + ":8000";
}
const BASEURL = "http://" + currentIP;

/* Definition of functions that are used on call by the event listeners */
// Fetches data from the backend
const fetchData = async (endpoint) => {
    try {
        const res = await fetch(`${BASEURL}/api/${endpoint}`);
        return await res.json();
    } catch (err) {
        alert(err);
    }
};

const initDataTable = async (tableName, options, listFunction) => {
    let dataTable;
    let isInit = false;

    if (isInit) {
        dataTable.destroy();
    }

    await listFunction();
    dataTable = $(`#${tableName}`).DataTable(options);
    isInit = true;
};

const populateTable = (data, tableBody, template) => {
    let content = ``;
    data.forEach((item) => {
        content += template(item);
    });
    tableBody.innerHTML = content;
};

const dataTablePlaysOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [4, 5] },
        { searchable: false, targets: [5] }
    ],
    pageLength: 10,
    destroy: true,
};

const dataTableSanctionsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [0, 1, 3, 4, 5] },
        { searchable: false, targets: [0, 1, 2, 3, 4, 5] }
    ],
    pageLength: 10,
    destroy: true,
};

const playsTemplate = (play) => `
    <tr>
        <td>${play.id}</td>
        <td>${play.student_id}</td>
        <td>${play.game__name}</td>
        <td>${play.time}</td>
        <td>${play.ended ? "<i class='fa-solid fa-check' style='color:green;'></i>" : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}</td>
        <td>
            <button class='btn btn-sm btn-danger delete-play' data-id='${play.id}'><i class='fa-solid fa-trash-can'></i></button>
        </td>
    </tr>
`;

const sanctionsTemplate = (sanction) => `
    <tr>
        <td>${sanction.id}</td>
        <td>${sanction.student__id}</td>
        <td>${sanction.cause}</td>
        <td>${sanction.play_id}</td>
        <td>${sanction.start_time}</td>
        <td>${sanction.end_time}</td>
    </tr>
`;

const listPlays = async () => {
    const data = await fetchData("get-plays-list");
    populateTable(data.plays, document.getElementById("tableBody_plays"), playsTemplate);
};

const listSanctions = async () => {
    const data = await fetchData("get-sanctions-list");
    populateTable(data.sanctions, document.getElementById("tableBody_sanctions"), sanctionsTemplate);
};

const initDataTables = async () => {
    await initDataTable("plays-table", dataTablePlaysOptions, listPlays);
    await initDataTable("sanctions-table", dataTableSanctionsOptions, listSanctions);
};


// Helper function to delete elements
function confirmAndDelete(endpoint, id, message) {
    if (confirm(message)) {
        $.ajax({
            type: 'DELETE',
            url: `${BASEURL}/api/${endpoint}`,
            data: JSON.stringify({ id }),
            headers: {
                'X-CSRFToken': CSRFTOKEN
            },
            success: function (data) {
                console.log(data);
                location.reload();
            },
            error: function (error) {
                // Handle errors
                if (endpoint === 'student' || endpoint === 'game') {
                    alert(`No se puede borrar el ${endpoint} porque tiene partidas asociadas`);
                } else if (endpoint === 'user') {
                    alert("No se puede borrar el usuario");
                } else if (endpoint === 'play') {
                    alert("No se puede borrar la partida porque tiene sanciones asociadas");
                }
                console.error(error);
            }
        });
    }
}


/* Inits all functions, variables, etc. from here */
// On page load
window.addEventListener('load', async () => {
    await initDataTables();
});

// Play deletion
$(document).on('click', '.delete-play', function () {
    const playId = $(this).data('id');
    const message = '¿Seguro que quieres borrar la partida?';
    confirmAndDelete('play', playId, message);
});
