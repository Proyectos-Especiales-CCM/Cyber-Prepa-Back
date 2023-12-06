// base url of the server to make requests to the API
const baseUrl = window.location.origin;
// var to store all the game cards elements
var game_cards = $('.cyber__card');
// element containing the user info
const userInfoElement = $('#user-info')[0];
var user_username = '';
// div containing all the cards that will be populated with the games fetched from the server
const cyberCardsContainer = document.getElementById('cyberCards');
/* dict to store the number of players in each game like
    {
        game_id (key):
            players_count (value)
            players_ids (list of values)
    }
*/
const template = {
    players_count: 0,
    players: []
};
var games_data = {};
// boolean to check if fetchGameStartTimes() has been called, to avoid more than one interval running at the same time
var isFetchingGameStartTimes = false;
// If the user is authenticated, retrieve the username
if (userInfoElement) {
    user_username = userInfoElement.dataset.username;
}

// Variable to store the countdown interval so it can be cleared when the cards are reset
var countdownInterval;
// Fetch and create Countdowns for each game
async function initCountdowns(gameStartTimes) {

    // Update the count down every 1 second
    countdownInterval = setInterval(function () {

        // Get current's date and time
        var now = new Date().getTime();
        // Iterate though the items
        gameStartTimes.forEach(item => {
            // Set the date we're counting down to
            var countDownDate = item.date.getTime();

            // Find the distance between now and the count down date
            var distance = countDownDate - now;

            // Time calculations for minutes and seconds
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);

            var timeTextDisplay = minutes + "m " + seconds + "s ";

            if (hours > 0) {
                timeTextDisplay = hours + "h " + timeTextDisplay;
            }

            // Display the result in the element with id="demo"
            var id = "cyber__countdown__" + (item.game_id);

            // If the count down is finished, write some text
            if (distance < 0 && games_data[item.game_id].players_count > 0) {
                document.getElementById(id).innerHTML = "AGOTADO";
            } else if (games_data[item.game_id].players_count === 0) {
                document.getElementById(id).innerHTML = "LIBRE";
            } else {
                document.getElementById(id).innerHTML = timeTextDisplay;
            }
        });
    }, 1000);
}

// Find and return the game_id (int) where the student_id (string) is playing
function findGameIdByPlayerId(playerId) {
    for (const gameId in games_data) {
        if (games_data.hasOwnProperty(gameId)) {
            const playersList = games_data[gameId].players;
            if (Array.isArray(playersList) && playersList.includes(playerId)) {
                // Return the game_id if the player is found in the players list
                return gameId;
            }
        }
    }
    // Return null if the player is not found in any game
    return null;
}

// Change a student from one game to another into the games_data dict
function changeToGame(playerId, newGameId) {
    // Check if the current game exists in games_data
    const currentGameId = findGameIdByPlayerId(playerId);

    if (games_data.hasOwnProperty(currentGameId)) {
        // Remove playerId from current game's players list if it exists
        const playerIndex = games_data[currentGameId].players.indexOf(playerId);
        if (playerIndex !== -1) {
            games_data[currentGameId].players.splice(playerIndex, 1);
        }
    }

    // Check if the new game exists in games_data
    if (games_data.hasOwnProperty(newGameId)) {
        // Add playerId to the new game's players list if it doesn't already exist
        if (!games_data[newGameId].players.includes(playerId)) {
            games_data[newGameId].players.push(playerId);
        }
    }
}

// Create the cards games from scratch
async function setGamesCards() {
    // Delete the previous cards and data
    cyberCardsContainer.innerHTML = '';
    games_data = {};
    // Fetch the games info from the server
    const data = await fetchGames(baseUrl);
    const games = data.games;

    // Create the cards
    games.forEach(game => {
        // Create the game_data with the game id as key using the template
        games_data[game.id] = { ...template };

        const card = document.createElement('div');
        
        card.className = 'cyber__card [ is-collapsed ]';
    
        const cardInner = document.createElement('div');
        cardInner.id = game.name;
        cardInner.className = 'cyber__card__inner [ js-expander ]';
        
        let playersCount = ``;
        if (game.players > 0) {
            playersCount = `<span>${game.players} jugadores</span><br>`;
            games_data[game.id].players_count = game.players;
        }

        if (user_username !== '' && game.plays_data !== undefined) {
            let ids_to_add = [];
            game.plays_data.forEach(player => {
                ids_to_add.push(player.student_id);
            });
            games_data[game.id].players = ids_to_add;
        }

        cardInner.innerHTML = `
            <span>${game.displayName}</span><br>
            <div id="cyber__game__players__count__${game.id}">
                ${playersCount}
            </div>
            <img class="cyber__image" src="/static/${game.file_route}" alt="${game.displayName}">
            <div class="remaining__time">
                <p id="cyber__countdown__${game.id}">No data</p>
            </div>
        `;

        card.appendChild(cardInner);
    
        // Check if the user is authenticated to add additional elements
        if (user_username !== '') {
            const plays_data = game.plays_data;
            let plays_data_html = ``;
            if (Array.isArray(plays_data)) {
                plays_data.forEach(player => {
                    plays_data_html += `
                        <div id="${player.student_id}" data-gameId="${game.id}" class="student draggable" draggable="true">
                            <li>${player.student_id}</li>
                            <form class="end-play-form" id="end-play-form-${player.student_id}">
                                <input type="hidden" name="student_id" value="${player.student_id}">
                                <input type="hidden" name="game_id" value="${game.id}">
                                <button type="submit" class="btn btn-success">End Play</button>
                            </form>
                            <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalSanciones" data-bs-matricula="${player.student_id}" >Sancionar</button>
                        </div>
                    `;
                });
            }

            const cardExpander = document.createElement('div');
            cardExpander.className = 'rounded cyber__card__expander';
            cardExpander.innerHTML = `
                <i class="fa fa-close [ js-collapser ]"></i>

                <form class="add-student-game mb-3" id="add-student-game-${game.id}">
                    <input type="hidden" name="game_id" value="${game.id}">
                    <input type="text" class="form-control" name="student_id" placeholder="ID estudiante" aria-label="ID estudiante" aria-describedby="basic-addon2">
                    <div class="input-group-append">
                        <button class="btn btn-outline-secondary" type="submit">Agregar estudiante</button>
                    </div>
                </form>

                <div class="collapsed__students">
                    <ul id="cyber__student__list__${game.id}" class="container__dropzone">
                        ${plays_data_html}
                    </ul>
                    <button class="scroll-button left">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-left-square-fill" viewBox="0 0 16 16">
                            <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm10.5 10V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4A.5.5 0 0 0 10.5 12z"/>
                        </svg>
                    </button>
                    <button class="scroll-button right">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-right-square-fill" viewBox="0 0 16 16">
                            <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm5.5 10a.5.5 0 0 0 .832.374l4.5-4a.5.5 0 0 0 0-.748l-4.5-4A.5.5 0 0 0 5.5 4v8z"/>
                        </svg>
                    </button>
                </div>
            `;
            card.appendChild(cardExpander);
        }
    
        // Append card to the container
        cyberCardsContainer.appendChild(card);
    });
}

// Retrieve the games cards info from the server
async function fetchGames(baseUrl) {
    let response = await fetch(baseUrl + "/api/get-games/");
    let obj = await response.json();
    return obj;
}

// Retrieve the games start times and games ids from the server
async function fetchGameStartTimes() {
    if (!isFetchingGameStartTimes) {
        isFetchingGameStartTimes = true;
        clearInterval(countdownInterval);
        try {
            let response = await fetch(baseUrl + "/api/get-games-start-time/");
            let obj = await response.json();

            const gameStartTimes = obj.map(item => ({
                date: new Date(item.time),
                game_id: item.game_id
            }));     
            initCountdowns(gameStartTimes);
        } catch (error) {
            console.error("There was an error fetching the game start times: " + error);
        } finally {
            isFetchingGameStartTimes = false;
        }
    }
}

// Create a new websocket to receive updates from the server
const updatesSocket = new WebSocket(`ws://${window.location.host}/ws/updates/`);

// Handle messages received from the server via the websocket
updatesSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const message = data['message'];
    const sender = data['sender'];

    // Only update the UI if the message was sent by another user
    if (sender !== user_username) {

        // If the user is not authenticated, only update the game cards accordingly
        if (user_username !== '') {
            if (message === 'Games updated') {
                resetAll();
            } else if (message === 'Plays updated') {
                console.log(data['info']);
                refreshStudentList(data['info']);
                fetchGameStartTimes();
            }
        } else {
            if (message === 'Games updated') {
                resetAll();
            } else if (message === 'Plays updated') {
                fetchGameStartTimes();
            }
        }
    }
};

// Handle closing the websocket
updatesSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

// Function to initialize the cards functionality for authenticated users
function initAuthCards() {
    game_cards = $('.cyber__card');
    initCardsFunctionality(game_cards);
    overrideEndPlayFormSubmit();
    overrideAddStudentFormSubmit();
    addScrollLeftRight();
}

// Creates and sets the functionality for the cards from scratch
async function resetAll(){
    await setGamesCards();
    await fetchGameStartTimes();
    if (user_username !== '') {
        initAuthCards();
    }
}

// On document load, create the cards from scratch
document.addEventListener('DOMContentLoaded', async () => {
    await resetAll();
});
