from django.shortcuts import render
from appointment.templatetags.appointment_tags import make_post_context

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def buildup(request):
    context= {
        "color": "default",
        "theme": "mentor_ds",
        "naver": "https://booking.naver.com/booking/13/bizes/441781",
        'basic_info': {
            'consult_email': 'hj3415@gmail.com'
        }
    }
    if request.method == 'GET':
        return render(request, f"home/home.html", context)
    elif request.method == "POST":
        context.update(make_post_context(request.POST, context['basic_info']['consult_email'], anchor='contact'))
        logger.info(context)
        return render(request, f"home/home.html", context)
