var $cell = $('.cyber__card');

// Fetch and create Countdowns
async function initCountdowns(gameStartTimes) {

    // Update the count down every 1 second
    var x = setInterval(function () {

        // Get current's date and time
        var now = new Date().getTime();
        for (let index = 1; index <= gameStartTimes.length; index++) {
            // Set the date we're counting down to
            var countDownDate = gameStartTimes[index - 1].getTime();

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
            var id = "cyber__countdown__" + (index);

            document.getElementById(id).innerHTML = timeTextDisplay;

            // If the count down is finished, write some text
            if (distance < 0) {
                //clearInterval(x);
                document.getElementById(id).innerHTML = "EXPIRED";
            }
        }
    }, 1000);
}

async function fetchGameStartTimes() {
    let currentIP = window.location.hostname;
    if (currentIP === "127.0.0.1" || currentIP === "localhost") {
        currentIP = currentIP + ":8000";
    }
    var file = "http://" + currentIP + "/api/get-games-start-time";
    let response = await fetch(file);
    let obj = await response.json();

    const gameStartTimes = obj.map(item => new Date(item.time));
    initCountdowns(gameStartTimes);
}

fetchGameStartTimes();
