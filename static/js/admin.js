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
                        <button class='btn btn-sm btn-danger'><i class='fa-solid fa-trash-can'></i></button>
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


// Inits datatable for students
let dataTableStudents;
let dataTableStudentsIsInit = false;

const dataTableStudentsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2] },
        { orderable: false, targets: [2] },
        { searchable: false, targets: [2] }
    ],
    pageLength: 10,
    destroy: true,
};
const initDataTableStudents = async () => {
    if (dataTableStudentsIsInit) {
        dataTableStudents.destroy();
    }
    await listStudents();
    dataTableStudents = $('#students-table').DataTable(dataTableStudentsOptions);
    dataTableStudentsIsInit = true;
};

const listStudents = async () => {
    try {
        let currentIP = window.location.hostname;
        if (currentIP === "127.0.0.1" || currentIP === "localhost") {
            currentIP = currentIP + ":8000";
        }
        var file = "http://" + currentIP + "/api/get-students-list";
        const res = await fetch(file)
        const data = await res.json()

        let content = ``;
        data.students.forEach((student) => {
            content += `
                <tr>
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>
                        <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
                        <button class='btn btn-sm btn-danger'><i class='fa-solid fa-trash-can'></i></button>
                    </td>
                </tr>
            `;
        });
        var tableBody_students = document.getElementById("tableBody_students");
        tableBody_students.innerHTML = content;
    } catch (err) {
        alert(err);
    }
};

// Inits datatable for games
let dataTableGames;
let dataTableGamesIsInit = false;

const dataTableGamesOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [0, 1, 2] },
        { searchable: false, targets: [0, 1, 2] }
    ],
    pageLength: 10,
    destroy: true,
};
const initDataTableGames = async () => {
    if (dataTableGamesIsInit) {
        dataTableGames.destroy();
    }
    await listGames();
    dataTableGames = $('#games-table').DataTable(dataTableGamesOptions);
    dataTableGamesIsInit = true;
};

const listGames = async () => {
    try {
        let currentIP = window.location.hostname;
        if (currentIP === "127.0.0.1" || currentIP === "localhost") {
            currentIP = currentIP + ":8000";
        }
        var file = "http://" + currentIP + "/api/get-games-list";
        const res = await fetch(file)
        const data = await res.json()

        let content = ``;
        data.games.forEach((game) => {
            content += `
                <tr>
                    <td>${game.id}</td>
                    <td>${game.name}</td>
                    <td>${game.displayName}</td>
                    <td>${game.available == true
                    ? "<i class='fa-solid fa-check' style='color:green;'></i>"
                    : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}
                    </td>
                    <td>${game.show == true
                    ? "<i class='fa-solid fa-check' style='color:green;'></i>"
                    : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}
                    </td>
                    <td>
                        <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
                        <button class='btn btn-sm btn-danger delete-game' data-id='${game.id}'><i class='fa-solid fa-trash-can'></i></button>
                    </td>
                </tr>
            `;
        });
        var tableBody_games = document.getElementById("tableBody_games");
        tableBody_games.innerHTML = content;
    } catch (err) {
        alert(err);
    }
};


// Inits datatable for logs
let dataTableLogs;
let dataTableLogsIsInit = false;

const dataTableLogsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3] },
        { orderable: false, targets: [0, 1, 3] },
        { searchable: false, targets: [0, 1, 2, 3] }
    ],
    pageLength: 10,
    destroy: true,
};
const initDataTableLogs = async () => {
    if (dataTableLogsIsInit) {
        dataTableLogs.destroy();
    }
    await listLogs();
    dataTableLogs = $('#logs-table').DataTable(dataTableLogsOptions);
    dataTableLogsIsInit = true;
};

const listLogs = async () => {
    try {
        let currentIP = window.location.hostname;
        if (currentIP === "127.0.0.1" || currentIP === "localhost") {
            currentIP = currentIP + ":8000";
        }
        var file = "http://" + currentIP + "/api/get-logs-list";
        const res = await fetch(file)
        const data = await res.json()

        let content = ``;
        data.logs.forEach((log) => {
            content += `
                <tr>
                    <td>${log.id}</td>
                    <td>${log.user__username}</td>
                    <td>${log.actionPerformed}</td>
                    <td>${log.time}</td>
                </tr>
            `;
        });
        var tableBody_logs = document.getElementById("tableBody_logs");
        tableBody_logs.innerHTML = content;
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
    await initDataTableStudents();
    await initDataTableGames();
    await initDataTableLogs();
    await initDataTableSanctions();
}

window.addEventListener('load', async () => {
    await initDataTables();
    var exampleModal = document.getElementById('exampleModal')
    exampleModal.addEventListener('show.bs.modal', function () { })

    // CSRF token
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Get current IP for AJAX requests
    let currentIP = window.location.hostname;
    if (currentIP === "127.0.0.1" || currentIP === "localhost") {
        currentIP = currentIP + ":8000";
    }
    const baseURL = "http://" + currentIP;

    // Game creation form
    $('#submitGame').click(function () {
        // Get form data
        var formData = $('#gameForm').serialize();
        console.log(formData)
        alert(formData);

        // Send data using AJAX
        $.ajax({
            type: 'POST',
            url: baseURL + '/api/game',
            data: formData,
            success: function (data) {
                //console.log(data);
                $('#exampleModal').modal('hide');

                // Reload the page to reflect the changes
                location.reload();
            },
            error: function (error) {
                // Handle errors
                console.error(error);
            }
        });
    });

    // Game deletion
    $('.delete-game').click(function () {
        var gameId = $(this).data('id');
        console.log('borrar juego')
        console.log('id',gameId);

        if (confirm('¿Seguro que quieres borrar el juego?')) {
            // Send an AJAX request to delete the game
            $.ajax({
                type: 'DELETE',
                url: baseURL + '/api/game',
                data: JSON.stringify({ id: gameId }),
                headers: {
                    'X-CSRFToken': csrftoken
                },
                success: function (data) {
                    console.log(data);
                    location.reload();
                },
                error: function (error) {
                    // Handle errors
                    console.error(error);
                }
            });
        }
    });

});