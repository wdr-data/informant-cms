const summarySelector = '.field-summary';
const textLabelSelector = '.field-text label';

const toggleSummary = (type) => {
    if (type === 'last' || type === 'breaking') {
        django.jQuery(summarySelector).hide();
        django.jQuery(textLabelSelector).html('Text:');
    } else {
        django.jQuery(summarySelector).show();
        django.jQuery(textLabelSelector).html('Facebook-Text:');
    }
}

django.jQuery(document).ready(function () {
    toggleSummary(django.jQuery(typeSelector)[0].value);
    django.jQuery(typeSelector).change(function () {
        toggleSummary(this.value);
    })
});
