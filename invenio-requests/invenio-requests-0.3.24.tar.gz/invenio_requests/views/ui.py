# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Request ui views module."""

from flask import Blueprint, current_app, render_template
from flask_login import current_user
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError

#
# Error handlers
#


def not_found_error(error):
    """Handler for 'Not Found' errors."""
    return render_template(current_app.config['THEME_404_TEMPLATE']), 404


def record_tombstone_error(error):
    """Tombstone page."""
    return render_template("invenio_requests/tombstone.html"), 410


def record_permission_denied_error(error):
    """Handle permission denier error on record views."""
    if not current_user.is_authenticated:
        # trigger the flask-login unauthorized handler
        return current_app.login_manager.unauthorized()
    return render_template(current_app.config['THEME_403_TEMPLATE']), 403


def create_ui_blueprint(app):
    """Register blueprint routes on app."""
    routes = app.config.get("REQUESTS_ROUTES")

    blueprint = Blueprint(
        "invenio_requests",
        __name__,
        template_folder="../templates",
        static_folder='../static'
    )

    # Register error handlers
    blueprint.register_error_handler(
        PermissionDeniedError,
        record_permission_denied_error,
    )
    blueprint.register_error_handler(
        PIDDeletedError,
        record_tombstone_error,
    )
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)

    return blueprint
