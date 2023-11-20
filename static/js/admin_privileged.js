/* Definition of functions that are used on call by the event listeners */
const dataTableStudentsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2] },
        { orderable: false, targets: [2] },
        { searchable: false, targets: [2] }
    ],
    pageLength: 10,
    destroy: true,
};

const dataTableGamesOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [0, 1, 2] },
        { searchable: false, targets: [0, 1, 2] }
    ],
    pageLength: 10,
    destroy: true,
};

const dataTableLogsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3] },
        { orderable: false, targets: [0, 1, 3] },
        { searchable: false, targets: [0, 1, 2, 3] }
    ],
    pageLength: 10,
    destroy: true,
};

const dataTableUsersOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3] },
        { orderable: false, targets: [0, 1, 2] },
        { searchable: false, targets: [0, 1] }
    ],
    pageLength: 10,
    destroy: true,
};

const studentTemplate = (student) => `
    <tr>
        <td>${student.id}</td>
        <td>${student.name}</td>
        <td>
            <button class='btn btn-sm btn-primary modify-student' data-bs-student-id='${student.id}' data-bs-student-name='${student.name}'><i class='fa-solid fa-pencil'></i></button>
            <button class='btn btn-sm btn-danger delete-student' data-id='${student.id}'><i class='fa-solid fa-trash-can'></i></button>
        </td>
    </tr>
`;

const gameTemplate = (game) => `
    <tr>
        <td>${game.id}</td>
        <td>${game.name}</td>
        <td>${game.displayName}</td>
        <td>${game.available ? "<i class='fa-solid fa-check' style='color:green;'></i>" : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}</td>
        <td>${game.show ? "<i class='fa-solid fa-check' style='color:green;'></i>" : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}</td>
        <td>
            <button class='btn btn-sm btn-primary modify-game' data-bs-game-id='${game.id}' data-bs-game-name='${game.name}' data-bs-game-displayname='${game.displayName}' data-bs-game-show='${game.show}'><i class='fa-solid fa-pencil'></i></button>
            <button class='btn btn-sm btn-danger delete-game' data-id='${game.id}'><i class='fa-solid fa-trash-can'></i></button>
        </td>
    </tr>
`;

const logTemplate = (log) => `
    <tr>
        <td>${log.id}</td>
        <td>${log.user__username}</td>
        <td>${log.actionPerformed}</td>
        <td>${log.time}</td>
    </tr>
`;

const userTemplate = (user) => `
    <tr>
        <td>${user.id}</td>
        <td>${user.username}</td>
        <td>${user.is_admin ? "<i class='fa-solid fa-check' style='color:green;'></i>" : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}</td>
        <td>
            <button class='btn btn-sm btn-primary modify-user' data-bs-user-id='${user.id}' data-bs-user-email='${user.email}' data-bs-user-is_admin='${user.is_admin ? "true" : "false"}'><i class='fa-solid fa-pencil'></i></button>
            <button class='btn btn-sm btn-danger delete-user' data-id='${user.id}'><i class='fa-solid fa-trash-can'></i></button>
        </td>
    </tr>
`;

const listStudents = async () => {
    const data = await fetchData("get-students-list");
    populateTable(data.students, document.getElementById("tableBody_students"), studentTemplate);
};

const listGames = async () => {
    const data = await fetchData("get-games-list");
    populateTable(data.games, document.getElementById("tableBody_games"), gameTemplate);
};

const listLogs = async () => {
    const data = await fetchData("get-logs-list");
    populateTable(data.logs, document.getElementById("tableBody_logs"), logTemplate);
};

const listUsers = async () => {
    const data = await fetchData("get-users-list");
    populateTable(data.users, document.getElementById("tableBody_users"), userTemplate);
};

// Inits all datatables
const initDataTablesPrivileged = async () => {
    await initDataTable("students-table", dataTableStudentsOptions, listStudents);
    await initDataTable("games-table", dataTableGamesOptions, listGames);
    await initDataTable("logs-table", dataTableLogsOptions, listLogs);
    await initDataTable("users-table", dataTableUsersOptions, listUsers);
}

// On page load
window.addEventListener('load', async () => {
    await initDataTablesPrivileged();
    // Modal, set values when editing
    var gameModal = document.getElementById('gameModal')
    gameModal.addEventListener('show.bs.modal', function () {
        $('#gameModalLabel').text('Nuevo juego');
        $('#submitGame').text('Crear');
        $('#name').val('');
        $('#displayName').val('');
        $('#show').removeAttr('checked');
    })
    var userModal = document.getElementById('userModal')
    userModal.addEventListener('show.bs.modal', function () {
        $('#userModalLabel').text('Nuevo usuario');
        $('#submitUser').text('Crear');
        $('#email').val('');
        $('#password').prop('required', true);
        $('#password2').prop('required', true);
        $('#is_admin').removeAttr('checked');
    })

    // Game creation form
    $('#submitGame').off('click').click(function () {
        // Get form data
        var formData = $('#gameForm').serialize();

        // Send data using AJAX
        $.ajax({
            type: 'POST',
            url: BASEURL + '/api/game/',
            data: formData,
            success: function (data) {
                //console.log(data);
                $('#gameModal').modal('hide');

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
    $('#submitUser').off('click').click(function () {
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
            url: BASEURL + '/api/user/',
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

// Student modify
$(document).on('click', '.modify-student', function () {
    const studentId = $(this).data('bs-student-id');
    const studentName = $(this).data('bs-student-name');
    $('#studentModal').modal('show');
    $('#studentId').val(studentId);
    $('#studentName').val(studentName);
    

    // On form submit
    $('#submitStudent').off('click').click(function (event) {
        event.preventDefault();

        // Create JSON form data
        var formData = {
            id: studentId,
            name: $('#studentName').val(),
        }

        var jsonData = JSON.stringify(formData);

        // Send data using AJAX as JSON
        $.ajax({
            type: 'PATCH',
            url: BASEURL + '/api/student',
            data: jsonData,
            contentType: 'application/json', // Set the content type to JSON
            headers: {
                'X-CSRFToken': CSRFTOKEN
            },
            success: function (data) {
                $('#studentModal').modal('hide');

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
    const studentId = $(this).data('id');
    const message = '¿Seguro que quieres borrar este estudiante?';
    confirmAndDelete('student', studentId, message);
});

// Game modify
$(document).on('click', '.modify-game', function () {
    const gameId = $(this).data('bs-game-id');
    const gameName = $(this).data('bs-game-name');
    const gameDisplayName = $(this).data('bs-game-displayname');
    const gameShow = $(this).data('bs-game-show');
    $('#gameModal').modal('show');
    $('#gameModalLabel').text('Modificar juego');
    $('#submitGame').text('Modificar');
    $('#gameId').val(gameId);
    $('#name').val(gameName);
    $('#displayName').val(gameDisplayName);
    // Add the "checked" attribute if the game is shown
    if (gameShow === true) {
        $('#show').prop('checked', true);
    } else {
        $('#show').prop('checked', false);
    }

    // On form submit
    $('#submitGame').off('click').click(function (event) {
        event.preventDefault();

        // Create JSON form data
        var formData = {
            id: gameId,
        }

        if ($('#name').val() != gameName) {
            formData.name = $('#name').val();
        }

        if ($('#displayName').val() != gameDisplayName) {
            formData.displayName = $('#displayName').val();
        }

        if ($('#show').prop('checked') != gameShow) {
            formData.show = $('#show').prop('checked');
        }

        var jsonData = JSON.stringify(formData);

        // Send data using AJAX as JSON
        $.ajax({
            type: 'PATCH',
            url: BASEURL + '/api/game/',
            data: jsonData,
            contentType: 'application/json/', // Set the content type to JSON
            headers: {
                'X-CSRFToken': CSRFTOKEN
            },
            success: function (data) {
                $('#gameModal').modal('hide');

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

// Game deletion
$(document).on('click', '.delete-game', function () {
    const gameId = $(this).data('id');
    const message = '¿Seguro que quieres borrar este juego?';
    confirmAndDelete('game', gameId, message);
});

// User modify
$(document).on('click', '.modify-user', function () {
    const userId = $(this).data('bs-user-id');
    const email = $(this).data('bs-user-email');
    const is_admin = $(this).data('bs-user-is_admin');
    $('#userModal').modal('show');
    $('#userModalLabel').text('Modificar usuario');
    $('#submitUser').text('Modificar');
    $('#email').val(email);
    // Add the "checked" attribute if the user is an admin
    if (is_admin === true) {
        $('#is_admin').prop('checked', true);
    } else {
        $('#is_admin').prop('checked', false);
    }
    $('#password').prop('required', false);
    $('#password2').prop('required', false);

    // On form submit
    $('#submitUser').off('click').click(function (event) {
        event.preventDefault();

        // Creates formData object
        var formData = {
            id: userId,
        };

        // if email is modified, recheck if it's valid
        if ($('#email').val() != email) {
            // Use regex to check if email is valid
            var changedEmail = $('#email').val();
            var emailRegex = /\S+@\S+\.\S+/;
            if (!emailRegex.test(changedEmail)) {
                alert("El email no es válido");
                return;
            }

            // Create the username from the email
            const parts = changedEmail.split('@');
            const modfUsername = parts[0].toUpperCase();
            const modfEmail = parts.join('@');

            // Add both to formData
            formData.username = modfUsername;
            formData.email = modfEmail;
        }

        // If password is not empty, check if it's valid
        if ($('#password').val() != "") {
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

            // If password is valid, add it to formData
            formData.password = password;
        }

        // If is_admin and #is_admin are different, add the is_admin field to formData
        if ($('#is_admin').prop('checked') != is_admin) {
            formData.is_admin = $('#is_admin').prop('checked');
        }

        // Convert formData to JSON
        var jsonData = JSON.stringify(formData);

        // Send data using AJAX as JSON
        $.ajax({
            type: 'PATCH',
            url: BASEURL + '/api/user/',
            data: jsonData,
            contentType: 'application/json/', // Set the content type to JSON
            headers: {
                'X-CSRFToken': CSRFTOKEN
            },
            success: function (data) {
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

// User deletion
$(document).on('click', '.delete-user', function () {
    const userId = $(this).data('id');
    const message = '¿Seguro que quieres eliminar el acceso a este usuario?';
    confirmAndDelete('user', userId, message);
});