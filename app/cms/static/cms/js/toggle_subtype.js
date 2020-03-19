const typeSelector = '#id_type';
const subtypeSelector = '#id_subtype';
const subtypeRowSelector = '.field-subtype';
const HAS_SUBTYPES = ['last', 'breaking'];

const updateTargetUrl = (type) => {
    django.jQuery.fn.select2.amd.require(
        ["select2/utils"],
        function (Utils) {
            const elem = django.jQuery(subtypeSelector);
            const s2data = Utils.GetData(elem[0]);
            const baseUrl = window.location.origin;
            const targetUrl = new URL(s2data.select2.dataAdapter.ajaxOptions.url, baseUrl);
            targetUrl.searchParams.set('report_type', type);
            s2data.select2.dataAdapter.ajaxOptions.url = targetUrl.pathname + targetUrl.search;
    });
};

django.jQuery(document).ready(function(){
    let select2ref;
    const initialValue = django.jQuery(typeSelector)[0].value;
    if (HAS_SUBTYPES.includes(initialValue)) {
        updateTargetUrl(initialValue);
    } else {
        django.jQuery(subtypeRowSelector).hide();
    }

    django.jQuery(typeSelector).change(function(){
        const visible = HAS_SUBTYPES.includes(this.value);
        if (visible) {
            django.jQuery(subtypeRowSelector).show();
            updateTargetUrl(this.value);

            // Re-init s2 field, reset the value and open the selection
            select2ref = django.jQuery(subtypeSelector).select2();
            setTimeout(() => {
                select2ref.val(null).trigger('change');
                select2ref.select2('open');
            });
        } else {
            django.jQuery(subtypeRowSelector).hide();
        }
    })
});
