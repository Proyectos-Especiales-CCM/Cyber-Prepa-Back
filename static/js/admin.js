/* Definition of functions that are used on call by the event listeners */
// Inits datatable for plays
let dataTablePlays;
let dataTablePlaysIsInit = false;

const dataTablePlaysOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [4, 5] },
        { searchable: false, targets: [5] }
    ],
    pageLength: 10,
    destroy: true,
};
const initDataTablePlays = async () => {
    if (dataTablePlaysIsInit) {
        dataTablePlays.destroy();
    }
    await listPlays();
    dataTablePlays = $('#plays-table').DataTable(dataTablePlaysOptions);
    dataTablePlaysIsInit = true;
};

const listPlays = async () => {
    try {
        let currentIP = window.location.hostname;
        if (currentIP === "127.0.0.1" || currentIP === "localhost") {
            currentIP = currentIP + ":8000";
        }
        var file = "http://" + currentIP + "/api/get-plays-list";
        const res = await fetch(file)
        const data = await res.json()

        let content = ``;
        data.plays.forEach((play) => {
            content += `
                <tr>
                    <td>${play.id}</td>
                    <td>${play.student_id}</td>
                    <td>${play.game__name}</td>
                    <td>${play.time}</td>
                    <td>${play.ended == true
                    ? "<i class='fa-solid fa-check' style='color:green;'></i>"
                    : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}
                    </td>
                    <td>
                        <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
                        <button class='btn btn-sm btn-danger delete-play' data-id='${play.id}'><i class='fa-solid fa-trash-can'></i></button>
                    </td>
                </tr>
            `;
        });
        var tableBody_plays = document.getElementById("tableBody_plays");
        tableBody_plays.innerHTML = content;
    } catch (err) {
        alert(err);
    }
};


// Inits datatable for sactions
let dataTableSanctions;
let dataTableSanctionsIsInit = false;

const dataTableSanctionsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [0, 1, 3, 4, 5] },
        { searchable: false, targets: [0, 1, 2, 3, 4, 5] }
    ],
    pageLength: 10,
    destroy: true,
};
const initDataTableSanctions = async () => {
    if (dataTableSanctionsIsInit) {
        dataTableSanctions.destroy();
    }
    await listSanctions();
    dataTableSanctions = $('#sanctions-table').DataTable(dataTableSanctionsOptions);
    dataTableSanctionsIsInit = true;
};

const listSanctions = async () => {
    try {
        let currentIP = window.location.hostname;
        if (currentIP === "127.0.0.1" || currentIP === "localhost") {
            currentIP = currentIP + ":8000";
        }
        var file = "http://" + currentIP + "/api/get-sanctions-list";
        const res = await fetch(file)
        const data = await res.json()

        let content = ``;
        data.sanctions.forEach((sanction) => {
            content += `
                <tr>
                    <td>${sanction.id}</td>
                    <td>${sanction.student__id}</td>
                    <td>${sanction.cause}</td>
                    <td>${sanction.play_id}</td>
                    <td>${sanction.start_time}</td>
                    <td>${sanction.end_time}</td>
                </tr>
            `;
        });
        var tableBody_sanction = document.getElementById("tableBody_sanctions");
        tableBody_sanction.innerHTML = content;
    } catch (err) {
        alert(err);
    }
};


// Inits all datatables
const initDataTables = async () => {
    await initDataTablePlays();
    await initDataTableSanctions();
}


/* Inits all functions, variables, etc. from here */
// CSRF token
var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Get current IP for AJAX requests
let currentIP = window.location.hostname;
if (currentIP === "127.0.0.1" || currentIP === "localhost") {
    currentIP = currentIP + ":8000";
}
const baseURL = "http://" + currentIP;


// On page load
window.addEventListener('load', async () => {
    await initDataTables();
});

// Play deletion
$(document).on('click', '.delete-play', function () {
    // Get play id
    var playId = $(this).data('id');

    if (confirm('¿Seguro que quieres borrar la partida?')) {
        // Send an AJAX request to delete the play
        $.ajax({
            type: 'DELETE',
            url: baseURL + '/api/play',
            data: JSON.stringify({ id: playId }),
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (data) {
                console.log(data);
                location.reload();
            },
            error: function (error) {
                // Handle errors
                alert("No se puede borrar la partida porque tiene sanciones asociadas");
                console.error(error);
            }
        });
    }
});
