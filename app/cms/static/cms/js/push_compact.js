
(function ($) {
    $("document").ready(function () {
        // Reorder teasers into the middle
        target = $("#pushcompact_form > div > fieldset")[1];
        teasers = $("#teasers-group");
        teasers.insertAfter(target);

        // Remove promo by default
        $("div#form-0.inline-related.dynamic-form .inline-deletelink").click()
    });
})(django.jQuery);
