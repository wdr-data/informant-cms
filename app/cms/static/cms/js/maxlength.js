
const gen_maxlength = function () {
    $("input:text:not(.vTimeField, .vDateField)").maxlength();
    $("textarea").maxlength();
};

gen_maxlength();

$(".add-row > a").click(function() {
    $(".maxlength").remove();
    gen_maxlength();
});
