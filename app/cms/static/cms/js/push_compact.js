
(function ($) {
    $("document").ready(function () {
        // Reorder teasers into the middle
        target = $("#pushcompact_form > div > fieldset")[1];
        teasers = $("#teasers-group");
        teasers.insertAfter(target);
    });
})(django.jQuery);
