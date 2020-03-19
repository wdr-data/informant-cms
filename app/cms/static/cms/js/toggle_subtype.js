const typeSelector = '#id_type';
const subtypeSelector = '.field-subtype';

django.jQuery(document).ready(function(){
    if (django.jQuery(typeSelector)[0].value === 'last') {
        django.jQuery(subtypeSelector).show();
    } else {
        django.jQuery(subtypeSelector).hide();
    }
    django.jQuery(typeSelector).change(function(){
        const visible = this.value === 'last';
        if (visible) {
            django.jQuery(subtypeSelector).show();
        } else {
            django.jQuery(subtypeSelector).hide();
        }
    })
});
