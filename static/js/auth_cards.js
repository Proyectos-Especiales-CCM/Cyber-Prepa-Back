// Initializes the expandable feature of the cards
function initCardsFunctionality(cards) {
    // open and close card when clicked on card
    cards.find('.js-expander').click(function () {
        var $thisCell = $(this).closest('.cyber__card');
        var rect = $thisCell[0].getBoundingClientRect();

        // scrollTo(rect.top + window.scrollY);
        // $('html, body').animate({
        //     scrollTop: $thisCell.offset().top
        // }, );
        $('html, body').scrollTop($thisCell.offset().top);

        if ($thisCell.hasClass('is-collapsed')) {
            cards.removeClass('is-expanded').addClass('is-collapsed');
            $thisCell.removeClass('is-collapsed').addClass('is-expanded');
        } else {
            $thisCell.removeClass('is-expanded').addClass('is-collapsed');
        }
    });


    // close card when click on cross
    cards.find('.js-collapser').click(function () {
        var $thisCell = $(this).closest('.cyber__card');
        $thisCell.removeClass('is-expanded').addClass('is-collapsed');
    });
}

/*  Refresh the student list for an specific game, uses AJAX to fetch the
    data and updates the UI smoothly to prevent the card from collapsing
    and maintain the user experience
*/
function refreshStudentList(gameId) {
    // CSRF token
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Get the student list element
    const studentList = $(`#cyber__student__list__${gameId}`);

    // Fetch the student list data
    $.ajax({
        type: "GET",
        url: `/api/get-players/?game-id=${gameId}`,
        headers: {
            'X-CSRFToken': csrftoken
        },
        dataType: "json",
        success: async function (data) {
            // Handle successful response
            if (data.status === "success") {
                console.log("Student list updated successfully for a game");
                // Update the UI to reflect the new student list
                studentList.empty();
                data.players.forEach(play => {
                    const htmlToAppend = `
                    <div id="${play.student_id}" data-gameName="${play.game_name}" class="student draggable" draggable="true">
                        <li>${play.student_id}</li>
                        <form class="end-play-form" id="end-play-form-${play.student_id}">
                            <input type="hidden" name="student_id" value="${play.student_id}">
                            <input type="hidden" name="game_id" value="${play.game_id}">
                            <button type="submit" class="btn btn-success">Terminar</button>
                        </form>
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalSanciones" data-bs-matricula="${play.student_id}" >Sancionar</button>
                    </div>
                    `;
                    studentList.append(htmlToAppend);
                });

                // Update the players count
                const playersCount = $(`#cyber__game__players__count__${gameId}`);
                playersCount.empty();
                if (data.players.length > 0) {
                    playersCount.append(`<span>${data.players.length} jugadores</span><br>`);
                }
                games_data[gameId].players_count = data.players.length;

                // Update the UI
                overrideEndPlayFormSubmit();
                await fetchGameStartTimes();
            } else {
                console.error("Error: " + data.message);
            }
        },
        error: function (xhr, status, error) {
            console.error("Players list update failed:", status, error);
        },
    });
}

/*  Override the end play form submit default behavior to use
    AJAX, update the UI, and send a message to the updates socket
     This is to prevent the page from reloading when the form
     is submitted and keep the application state updated without
     interrupting the user experience
*/
function overrideEndPlayFormSubmit() {
    $(".end-play-form").off().submit(function(event) {
        event.preventDefault();
        const form = $(this);
        const studentId = form.find("input[name=student_id]").val();
        const gameId = form.find("input[name=game_id]").val();
        // CSRF token
        var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        $.ajax({
            type: "POST",
            url: "/api/set-play-ended/",
            data: form.serialize(),
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: "json",
            beforeSend: function (xhr, settings) {
                // Disable the submit button to prevent multiple submissions
                form.find("button[type=submit]").prop("disabled", true);
            },
            success: function (data) {
                // Handle successful response
                if (data.status === "success") {
                    console.log("Play ended successfully for student ID:", studentId);
                    // Perform any other actions you want after successfully setting the play as ended

                    // Remove the student element from the UI
                    const studentElement = form.closest(".student");
                    studentElement.remove();
                    updatesSocket.send(JSON.stringify({
                        'message': 'Plays updated',
                        'info': gameId,
                        'sender': user_username,
                    }));

                    // Update the players counter in the UI
                    games_data[gameId].players_count -= 1;
                    const playersCount = $(`#cyber__game__players__count__${gameId}`);
                    playersCount.empty();
                    if (games_data[gameId].players_count > 0) {
                        playersCount.append(`<span>${games_data[gameId].players_count} jugadores</span><br>`);
                    }

                } else {
                    console.error("Error: " + data.message);
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX request failed:", status, error);
            },
            complete: function () {
                // Re-enable the submit button after the request is complete
                form.find("button[type=submit]").prop("disabled", false);
            },
        });
    });
};

/*  Override the add student game form submit default behavior to use AJAX,
    update the UI, and send a message to the updates socket
     This is to prevent the page from reloading when the form
     is submitted and keep the application state updated without
     interrupting the user experience
*/
function overrideAddStudentFormSubmit() {
    // Game add student form
    $(".add-student-game").submit(function (event) {
        event.preventDefault();
        const form = $(this);
        const gameId = form.find("input[name=game_id]").val();
        const studentId = form.find("input[name=student_id]").val();
        // CSRF token
        var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        $.ajax({
            type: "POST",
            url: "/api/add-student-to-game/",
            data: form.serialize(),
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: "json",
            beforeSend: function (xhr, settings) {
                // Disable the submit button to prevent multiple submissions
                form.find("button[type=submit]").prop("disabled", true);
                // Hide the error alert before sending the request
                $("#error-alert").addClass("d-none");
            },
            success: async function (data) {
                // Handle successful response
                if (data.status === "success") {
                    // Update the UI to reflect the added student
                    const studentList = form.nextAll('.collapsed__students').first().children('ul');
                    const htmlToAppend = `
                    <div id="${studentId}" data-gameId="${gameId}" class="student draggable" draggable="true">
                        <li>${studentId}</li>
                        <form class="end-play-form" id="end-play-form-${studentId}">
                            <input type="hidden" name="student_id" value="${studentId}">
                            <input type="hidden" name="game_id" value="${gameId}">
                            <button type="submit" class="btn btn-success">Terminar</button>
                        </form>
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalSanciones" data-bs-matricula="${studentId}" >Sancionar</button>
                    </div>
                    `;

                    if (data.message === "Alumno cambiado de juego") {
                        old_game_id = findGameIdByPlayerId(studentId);
                        // Delete the student from the old game
                        $(`#${studentId}`).remove();
                        changeToGame(studentId, gameId);
                        games_data[old_game_id].players_count -= 1;
                        const oldPlayersCount = $(`#cyber__game__players__count__${old_game_id}`);
                        oldPlayersCount.empty();
                        if (games_data[old_game_id].players_count > 0) {
                            oldPlayersCount.append(`<span>${games_data[old_game_id].players_count} jugadores</span><br>`);
                        }

                        // Send a message to the updates socket
                        updatesSocket.send(JSON.stringify({
                            'message': 'Plays updated',
                            'info': old_game_id,
                            'sender': user_username,
                        }));
                        console.log("Student changed to game successfully:", studentId);
                    } else {
                        console.log("Student added to game successfully:", studentId);
                    }

                    studentList.append(htmlToAppend);
                    // Update the players counter in the UI
                    games_data[gameId].players_count += 1;
                    const playersCount = $(`#cyber__game__players__count__${gameId}`);
                    playersCount.empty();
                    if (games_data[gameId].players_count > 0) {
                        playersCount.append(`<span>${games_data[gameId].players_count} jugadores</span><br>`);
                    }

                    // Send a message to the updates socket
                    updatesSocket.send(JSON.stringify({
                        'message': 'Plays updated',
                        'info': gameId,
                        'sender': user_username,
                    }));

                    // Refresh the UI functionality
                    overrideEndPlayFormSubmit();
                    await fetchGameStartTimes();
                } else {
                    console.error("Error: " + data.message);

                    // Display the error message in the alert
                    $("#error-alert").text(data.message);
                    $("#error-alert").removeClass("d-none");

                    setTimeout(function () {
                        $("#error-alert").addClass("d-none");
                    }, 3000);
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX request failed:", status, error);
            },
            complete: function () {
                // Clear the student ID input and re-enable the submit button after the request is complete
                form.find("input[name=student_id]").val("");
                form.find("button[type=submit]").prop("disabled", false);
            },
        });
    });
};

/* Store the players data in a dictionary to keep track of the
    players in each game and update the UI accordingly
*/
async function fetchAllPlayers() {
    // Fetch the players data
    const data = await fetchData("get-players-list");
    // Store the players data in a dictionary
    data.players.forEach(play => {
        if (playersList[play.game_id] === undefined) {
            playersList[play.game_id] = [];
        }
        playersList[play.game_id].push(play);
    });
}
