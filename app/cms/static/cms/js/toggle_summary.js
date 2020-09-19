const summarySelector = '.field-summary';
const textLabelSelector = '.field-text label';
const fieldsetSelectorTelegram = 'fieldset.telegram';
const fieldsetSelectorFacebook = 'fieldset.facebook h2';
const fieldsetSelectorAll = 'fieldset.all';

const toggleSummary = (type) => {
    if (type === 'evening' || type === 'breaking' || type === 'last') {
        django.jQuery(summarySelector).hide();
        django.jQuery(textLabelSelector).html('Text:');
        django.jQuery(fieldsetSelectorTelegram).hide();
        django.jQuery(fieldsetSelectorFacebook).hide();
        django.jQuery(fieldsetSelectorAll).css('margin-bottom', '0px');
    } else {
        django.jQuery(summarySelector).show();
        django.jQuery(textLabelSelector).html('Facebook-Text:');
        django.jQuery(fieldsetSelectorTelegram).show();
        django.jQuery(fieldsetSelectorFacebook).show();
        django.jQuery(fieldsetSelectorAll).css('margin-bottom', '');
    }
}

django.jQuery(document).ready(function () {
    toggleSummary(django.jQuery(typeSelector)[0].value);
    django.jQuery(typeSelector).change(function () {
        toggleSummary(this.value);
    })
});
