// open and close card when clicked on card
$cell.find('.js-expander').click(function () {
    var $thisCell = $(this).closest('.cyber__card');

    if ($thisCell.hasClass('is-collapsed')) {
        $cell.removeClass('is-expanded').addClass('is-collapsed');
        $thisCell.removeClass('is-collapsed').addClass('is-expanded');
    } else {
        $thisCell.removeClass('is-expanded').addClass('is-collapsed');
    }
});

// close card when click on cross
$cell.find('.js-collapser').click(function () {
    var $thisCell = $(this).closest('.cyber__card');
    $thisCell.removeClass('is-expanded').addClass('is-collapsed');
});

// Student end play form
$(document).ready(function () {
    $(".end-play-form").submit(function (event) {
        event.preventDefault();
        const form = $(this);
        const studentId = form.find("input[name=student_id]").val();

        $.ajax({
            type: "POST",
            url: "/api/set-play-ended",
            data: form.serialize(),
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

    // Game add student form
    $(".add-student-game").submit(function (event) {
        event.preventDefault();
        const form = $(this);
        const gameId = form.find("input[name=game_id]").val();
        const studentId = form.find("input[name=student_id]").val();

        $.ajax({
            type: "POST",
            url: "/api/add-student-to-game",
            data: form.serialize(),
            dataType: "json",
            beforeSend: function (xhr, settings) {
                // Disable the submit button to prevent multiple submissions
                form.find("button[type=submit]").prop("disabled", true);
                // Hide the error alert before sending the request
                $("#error-alert").addClass("d-none");
            },
            success: function (data) {
                // Handle successful response
                if (data.status === "success") {
                    console.log("Student added to game successfully:", studentId);

                    // Optionally, update the UI to reflect the added student
                    const studentList = form.siblings("ul");
                    studentList.append('<div class="student draggable" draggable="true"><li>' + studentId + '</li></div>');
                } else {
                    console.error("Error: " + data.message);

                    // Display the error message in the alert
                    $("#error-alert").text(data.message);
                    $("#error-alert").removeClass("d-none");
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
});