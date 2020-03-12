(function ($) {
    $('form').submit(function() {
        $(this).find(':submit').prop('disabled', true);
    });
})(django.jQuery);
