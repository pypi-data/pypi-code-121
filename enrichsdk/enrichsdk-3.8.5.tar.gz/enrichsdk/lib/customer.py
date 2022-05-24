import os
import sys
import json
import logging
import traceback

logger = logging.getLogger("app")


def should_skip(name):

    return name.startswith(".") or name == "__pycache__"


def load_customer_assets(context={}):
    """
    Go through the customer directories and add the assets from all
    installed customer modules.

    The ENRICH_CUSTOMERS looks like system path, and it is processed
    as such. It gives priority to the modules earlier in the path
    than later. Typically you create a run directory and prepend
    that run directory in front of the standard directory.
    """

    assets = {}

    # Check if the environment is correctly configured
    enrich_customers = context.get(
        "ENRICH_CUSTOMERS", os.environ.get("ENRICH_CUSTOMERS", None)
    )

    if enrich_customers is None:
        enrich_root = context.get("ENRICH_ROOT", os.environ.get("ENRICH_ROOT", None))
        if enrich_root is not None:
            enrich_customers = os.path.join(enrich_root, "customers")

    if enrich_customers is None:
        logger.error("Customer root is missing : {}".format(enrich_customers))
        return assets

    # => Collect all possible paths..
    customer_roots = {}
    for customer_root in enrich_customers.split(";"):
        if not os.path.exists(customer_root):
            continue
        for customer in os.listdir(customer_root):
            if customer not in customer_roots:
                customer_roots[customer] = os.path.join(customer_root, customer)

    # Now go through each of them...
    for customer, customer_dir in customer_roots.items():

        # customer : scribble
        # customer_dir : $ENRICH_ROOT/customers/scribble

        # parent : $ENRICH_ROOT/customers
        customer_root = os.path.dirname(customer_dir)

        if not os.path.isdir(customer_dir) or should_skip(customer):
            continue

        enrichfile = os.path.join(customer_dir, "enrich.json")
        if not os.path.exists(enrichfile):
            logger.debug("Missing enrichfile. Skipping customer: {}".format(customer))
            continue

        try:
            enrich = json.load(open(enrichfile))
        except:
            logger.debug("Invalid enrichfile. Skipping customer: {}".format(customer))
            continue

        if not enrich.get("enable", True):
            logger.debug("Disabled customer. Skipping customer: {}".format(customer))
            continue

        for usecase in os.listdir(customer_dir):
            """
            Each usecase within the customer organization
            """
            usecasedir = os.path.join(customer_dir, usecase)

            if not os.path.isdir(usecasedir) or should_skip(usecase):
                continue

            enrichfile = os.path.join(usecasedir, "enrich.json")

            if not os.path.exists(enrichfile):
                logger.debug(
                    "Missing enrichfile. Skipping usecase: {}:{}".format(
                        customer, usecase
                    )
                )
                continue

            try:
                enrich = json.load(open(enrichfile))
            except:
                logger.debug(
                    "Invalid enrichfile. Skipping usecase: {}:{}".format(
                        customer, usecase
                    )
                )

            if not enrich.get("enable", True):
                logger.debug(
                    "Disabled org. Skipping usecase: {}:{}".format(customer, usecase)
                )
                continue

            # => Check assets
            # Contrib
            #        /pkg
            #            /assets
            #        /assets

            for assetsdir in [
                os.path.join(usecasedir, "pkg", "assets"),
                os.path.join(usecasedir, "assets"),
            ]:
                if not os.path.exists(assetsdir):
                    continue

                for a in os.listdir(assetsdir):
                    if should_skip(a):
                        continue

                    for pkgdir in [
                        os.path.join(assetsdir, a, a),
                        os.path.join(assetsdir, a, "src", a),
                    ]:

                        if not os.path.exists(pkgdir):
                            continue

                        libdir = os.path.abspath(os.path.dirname(pkgdir))
                        if libdir not in sys.path:
                            sys.path.append(libdir)

                        assets[a] = {
                            "fullpath": os.path.join(libdir, a),
                            "relpath": os.path.relpath(
                                os.path.join(libdir, a), customer_root
                            ),
                            "organization": enrich["org"]["name"],
                            "usecase": usecase,
                            "customer": customer,
                        }

    return assets


def find_usecase(path):
    """
    Given any filepath, find the usecase corresponding to it.
    """
    try:

        # Look through the loaded usecases from settings.
        from django.conf import settings

        path = os.path.realpath(path)
        for usecase in settings.USECASES:
            usecase_root = os.path.realpath(usecase["root"])
            if os.path.commonprefix([path, usecase_root]) == usecase_root:
                return usecase
    except:
        logger.exception("Could not find the usecase for the path")

    return None
