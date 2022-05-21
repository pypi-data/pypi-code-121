import os
from django.shortcuts import render, get_object_or_404
#from .models import Portfolio
from django.conf import settings

import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def details(request, id: int):
    context = {

        }
    logger.debug(context)
    return render(request, f"courses_details/details.html", context)
