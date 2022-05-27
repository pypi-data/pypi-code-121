from django import template
from django.template.loader import render_to_string
# from django_driverjs.Driverjs.models import Driver
from Driverjs.serializers import DriverSerializer, DriverStepSerializer
from django.apps import apps
get_model = apps.get_model
Driver = get_model('Driverjs', 'Driver')


register = template.Library()

@register.simple_tag(takes_context=True)
def setup_driver(context, slug,tag=True):
    ctx = context.flatten()
    try:
        driver = Driver.objects.get(slug=slug)
    except Driver.DoesNotExist:
        return ''

    d = DriverSerializer(driver).data
    driver_options = {}
    for item in d:
        if d[item]:
            driver_options[item]= d[item]
            if type(d[item]) == bool:
                driver_options[item] = str(d[item]).lower()
    ctx['driver'] = driver


    ctx['driver_options'] = driver_options

    driver_steps = []
    
    for step in driver.driversteps.all():
        ds = DriverStepSerializer(step).data
        ds_t = {}
        popover = {}
        not_popover= ['element','stageBackground','onHighlightStarted','onHighlighted','onDeselected','onReset','onNext','onPrevious']
        for item in ds:
            if ds[item]:
                if item in not_popover:
                    ds_t[item]= ds[item]
                    if type(ds[item]) == bool:
                        ds_t[item] = str(ds[item]).lower()
                else:
                    popover[item]= ds[item]
                    if type(ds[item]) == bool:
                        popover[item] = str(ds[item]).lower()

        ds_t['popover'] = popover
        driver_steps.append(ds_t)
    ctx['driver_steps'] = driver_steps
    ctx['tag'] = tag
    result = render_to_string('Driverjs/driver_js.html', ctx)
    return result
