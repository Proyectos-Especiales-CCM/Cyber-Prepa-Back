/* Definition of functions that are used on call by the event listeners */
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
                        <button class='btn btn-sm btn-danger delete-student' data-id='${student.id}'><i class='fa-solid fa-trash-can'></i></button>
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


// Inits datatable for users
let dataTableUsers;
let dataTableUsersIsInit = false;

const dataTableUsersOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3] },
        { orderable: false, targets: [0, 1, 2] },
        { searchable: false, targets: [0, 1] }
    ],
    pageLength: 10,
    destroy: true,
};
const initDataTableUsers = async () => {
    if (dataTableUsersIsInit) {
        dataTableUsers.destroy();
    }
    await listUsers();
    dataTableUsers = $('#users-table').DataTable(dataTableUsersOptions);
    dataTableUsersIsInit = true;
};

const listUsers = async () => {
    try {
        let currentIP = window.location.hostname;
        if (currentIP === "127.0.0.1" || currentIP === "localhost") {
            currentIP = currentIP + ":8000";
        }
        var file = "http://" + currentIP + "/api/get-users-list";
        const res = await fetch(file)
        const data = await res.json()

        let content = ``;
        data.users.forEach((user) => {
            content += `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.is_admin == true
                    ? "<i class='fa-solid fa-check' style='color:green;'></i>"
                    : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}
                    </td>
                    <td>
                        <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
                        <button class='btn btn-sm btn-danger delete-user' data-id='${user.id}'><i class='fa-solid fa-trash-can'></i></button>
                    </td>
                </tr>
            `;
        });
        var tableBody_user = document.getElementById("tableBody_users");
        tableBody_user.innerHTML = content;
    } catch (err) {
        alert(err);
    }
};


// Inits all datatables
const initDataTablesPrivileged = async () => {
    await initDataTableStudents();
    await initDataTableGames();
    await initDataTableLogs();
    await initDataTableUsers();
}

// On page load
window.addEventListener('load', async () => {
    await initDataTablesPrivileged();
    // Modal, set values when editing
    var exampleModal = document.getElementById('exampleModal')
    exampleModal.addEventListener('show.bs.modal', function () { })

    // Game creation form
    $('#submitGame').click(function () {
        // Get form data
        var formData = $('#gameForm').serialize();

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

    // User creation form
    $('#submitUser').click(function () {
        // Get form data
        var formData = $('#userForm').serialize();

        // Use regex to check if email is valid
        var email = $('#email').val();
        var emailRegex = /\S+@\S+\.\S+/;
        if (!emailRegex.test(email)) {
            alert("El email no es válido");
            return;
        }
        // Make email before the @ uppercase and add it to formData
        var parts = email.split('@');
        parts[0] = parts[0].toUpperCase();
        // Add to formData the username as the value of the email before the @ with capital letters
        formData += "&username=" + parts[0];
        // Add to formData the email with the username in uppercase
        var modifiedEmail = parts.join('@');
        $('#email').val(modifiedEmail);
        formData += "&email=" + modifiedEmail;

        // Check if passwords aren't empty & match
        var password = $('#password').val();
        var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
        if (!passwordRegex.test(password)) {
            alert("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número");
            return;
        }

        var password2 = $('#password2').val();
        if (password != password2) {
            alert("Las contraseñas no coinciden");
            return;
        }

        // Send data using AJAX
        $.ajax({
            type: 'POST',
            url: baseURL + '/api/user',
            data: formData,
            success: function (data) {
                //console.log(data);
                $('#userModal').modal('hide');

                // Reload the page to reflect the changes
                location.reload();
            },
            error: function (error) {
                // Handle errors
                console.error(error);
            }
        });
    });
});

// Student deletion
$(document).on('click', '.delete-student', function () {
    // Get student id
    var studentId = $(this).data('id');

    if (confirm('¿Seguro que quieres borrar este estudiante?')) {
        // Send an AJAX request to delete the student
        $.ajax({
            type: 'DELETE',
            url: baseURL + '/api/student',
            data: JSON.stringify({ id: studentId }),
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (data) {
                console.log(data);
                location.reload();
            },
            error: function (error) {
                // Handle errors
                alert("No se puede borrar el estudiante porque tiene partidas asociadas");
                console.error(error);
            }
        });
    }
});

// Game deletion
$(document).on('click', '.delete-game', function () {
    // Get game id
    var gameId = $(this).data('id');

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
                alert("No se puede borrar el juego porque tiene partidas asociadas");
                console.error(error);
            }
        });
    }
});

// User deletion
$(document).on('click', '.delete-user', function () {
    // Get user id
    var userId = $(this).data('id');

    if (confirm('¿Seguro que quieres eliminar el acceso a este usuario?')) {
        // Send an AJAX request to delete (deactivate) the user
        $.ajax({
            type: 'DELETE',
            url: baseURL + '/api/user',
            data: JSON.stringify({ id: userId }),
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (data) {
                console.log(data);
                location.reload();
            },
            error: function (error) {
                // Handle errors
                alert("No se puede borrar el usuario");
                console.error(error);
            }
        });
    }
});