from os import environ

# Mail settings
ADMINS = [
    ("Admin", environ.get("EMAIL_ADMIN", "admin@otree.survey")),
]
EMAIL_HOST = environ.get("EMAIL_HOST", None)
EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD", None)
EMAIL_USE_SSL = bool(environ.get("EMAIL_USE_SSL", 1))
EMAIL_PORT = int(environ.get("EMAIL_PORT", 465))
EMAIL_SUBJECT_PREFIX = "[oTree] "
EMAIL_TIMEOUT = 2  # connection attempt is blocking event -> set timeout to 2 seconds

# Add custom logger to standard oTree settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_fale": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "otree_survey.errors.email.CustomAdminEmailHandler",
            "filters": [],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
