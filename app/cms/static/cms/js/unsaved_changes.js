
var unsaved = false;

function unloadPage() {
    if (unsaved) {
        return "Du hast ungespeicherte Änderungen!";
    }
}

window.onbeforeunload = unloadPage;

(function ($) {
    $("document").ready(function () {
        $(":input").change(function () { //trigers change in all input fields including text type
            unsaved = true;
        });

        $('.submit-row > input').click(function () {
            unsaved = false;
        });
    });
})(django.jQuery);
