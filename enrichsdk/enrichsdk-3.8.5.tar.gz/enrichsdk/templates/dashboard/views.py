import os
import sys
import io
import json
import copy
import logging
import string
import random
import csv
import gzip
import hashlib
import math
import traceback
import tempfile
import gc
import sqlite3
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from dateutil import parser as dateparser
import pandas as pd
import numpy as np

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMultiAlternatives
import enrichsdk

from celery.result import AsyncResult
from celery import current_app

from users.decorators import log_activity
from enrichsdk.lib.customer import find_usecase

from .tasks import complex_task

logger = logging.getLogger("app")

usecase = find_usecase(__file__)


def index(request, spec):
    return render(
        request,
        "APPNAME/index.html",
        {
            "usecase": usecase,
        },
    )


@log_activity("complex", nature="application")
def complex_request(request, spec):
    """
    Use this for workflows.
    """

    post = request.POST.dict()
    params = post["params"]
    referrer = post["referrer"]
    try:

        # Gather the parameters
        params = json.loads(params)
        name = params.get("name", "")
        dt = datetime.now().date().isoformat()
        name = f"complex-{name}-{dt}"
        # Now look for transactions
        result = complex_task.delay(
            {
                "name": name,
                "source": params.get("source", ""),
            }
        )

    except:
        logger.exception("Internal error")
        messages.error(request, "Error while searching. Check log")
        return HttpResponseRedirect(referrer)

    try:
        resulturl = (
            reverse("APPNAME:txnsearch_result")
            + "?"
            + urlencode({"task_id": result.id, "referrer": referrer})
        )

        return HttpResponseRedirect(resulturl)
    except:
        logger.exception("Unable to issue a background task")
        messages.error(request, "Unable to issue a background task")
        return HttpResponseRedirect(referrer)


def complex_result(request, spec):
    """
    Show the results...
    """

    task_id = request.GET.get("task_id", None)
    referrer = request.GET.get("referrer", None)
    download = request.GET.get("download", None)
    download = str(download) == "true"

    # Handle invalid referrer...
    if referrer is None:
        messages.warning(request, f"No referrer")
        referrer = reverse("APPNAME:index")

    # Sanity check
    if task_id is None:
        messages.error(request, f"Empty task id")
        return HttpResponseRedirect(referrer)

    thisurl = (
        reverse("APPNAME:complex_result")
        + "?"
        + urlencode({"task_id": task_id, "referrer": referrer})
    )

    try:

        task_result = AsyncResult(task_id)

        value = task_result.result
        if not isinstance(value, dict):
            value = str(value)

        result = {
            "id": task_id,
            "status": task_result.status,
            "result": value,
            "args": task_result.args,
        }

    except:
        logger.exception("Unable to access result")
        messages.warning(request, f"Internal error. Invalid task")
        return HttpResponseRedirect(referrer)

    if download:

        if result["status"] != "SUCCESS":
            messages.error(request, f"Download only supported for successful runs")
            return HttpResponseRedirect(thisurl)

        # Now good to go
        records = result["result"]["records"]
        if len(records) == 0:
            messages.error(request, f"No matches found")
            return HttpResponseRedirect(referrer)

        name = result["args"][0].get("name", "complex-task-{task_id}.csv")
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{name}"'

        # Write the content...
        writer = csv.writer(response)
        for r in records:
            writer.writerow(r)

        # This renders the csv...
        return response

    return render(
        request,
        "APPNAME/complex_task_result.html",
        {
            "usecase": usecase,
            "task": result,
            "referrer": referrer,
        },
    )
