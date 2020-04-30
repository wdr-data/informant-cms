const typeSelector = '#id_type';
const subtypeSelector = '.field-subtype';

const toggleSubtype = (type) => {
    if (type === 'last') {
        django.jQuery(subtypeSelector).show();
    } else {
        django.jQuery(subtypeSelector).hide();
    }
}

django.jQuery(document).ready(function () {
    toggleSubtype(django.jQuery(typeSelector)[0].value);

    django.jQuery(typeSelector).change(function () {
        toggleSubtype(this.value);
    })
});
