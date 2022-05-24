PYPERS_RUN_CONFIG = {
    'name': 'gbd_pypers_run_config',
    'indexes': [
        [
            {'name': 'runid',
             'type': str,
             'primary_index': True
             },
            {'name': 'collection',
             'type': str,
             'primary_index': False}
        ],
    ],
    'ttl': 3  # in days
}

PYPERS_RUN_CONFIG_STEPS = {
    'name': 'gbd_pypers_run_config_steps',
    'indexes': [
        [
            {'name': 'runid_collection',
             'type': str,
             'primary_index': True
             },
            {'name': 'step_name',
             'type': str,
             'primary_index': False}
        ],
    ],
    'ttl': 3  # in days

}

PYPERS_INDEXING_CONFIG = {
    'name': 'gbd_config',
    'indexes': [
        [
            {'name': 'uid',
             'type': int,
             'primary_index': True
             },
        ],
    ]
}

PYPERS_DONE_ARCHIVE = {
    'name': 'gbd_pypers_done_archive',
    'indexes': [
        [
            {'name': 'gbd_collection',
             'type': str,
             'primary_index': True},
            {'name': 'archive_name',
             'type': str,
             'primary_index': False}
        ],
    ]
    }

PYPERS_SEEN_STEPS = {
    'name': 'gbd_pypers_seen_steps',
    'indexes': [
        [
            {'name': 'runid',
             'type': str,
             'primary_index': True
             },
            {'name': 'collection',
             'type': str,
             'primary_index': False}
        ],
    ],
    'ttl': 3  # in days

}

PYPES_ERRORS = {
    'name': 'gbd_pypers_errors',
    'indexes': [
        [
            {'name': 'time',
             'type': str,
             'primary_index': True
             }
        ],
    ]
}

PYPERS_LOGS = {
    'name': 'gbd_pypers_logs',
    'indexes': [
        [
            {'name': 'runid_collection',
             'type': str,
             'primary_index': True
             },
            {'name': 'log_time',
             'type': str,
             'primary_index': False}
        ],
    ],
    'ttl': 3  # in days
}

PYPERS_CONFIG = {
    'name': 'gbd_pypers_config',
    'indexes': [
        [
            {'name': 'name',
             'type': str,
             'primary_index': True
             },
        ],
    ]
}

PYPERS_PRE_PROD = {
    'name': 'gbd_docs_live',
    'read': 10,
    'write': 10,
    'max_write': 200,
    'max_read': 200,
    'indexes': [
        [

            {'name': 'st13',
             'type': str,
             'primary_index': True}
        ],
        [
            {'name': 'latest_run_id',
             'type': str,
             'primary_index': True},
            {'name': 'st13',
             'type': str,
             'primary_index': False}
        ],
        [
            {'name': 'gbd_collection',
             'type': str,
             'primary_index': True},
            {'name': 'st13',
             'type': str,
             'primary_index': False}
        ]
    ]
    }


PYPERS_PRE_PROD_HISTORY = {
    'name': 'gbd_docs_copies',
    'read': 5,
    'write': 10,
    'max_write': 200,
    'max_read': 50,
    'indexes': [
        [
            {'name': 'st13',
             'type': str,
             'primary_index': True},
            {'name': 'office_extraction_date',
             'type': str,
             'primary_index': False}
        ],
        [
            {'name': 'office_extraction_date',
             'type': str,
             'primary_index': True},
            {'name': 'st13',
             'type': str,
             'primary_index': False},
        ],
        [
            {'name': 'run_id',
             'type': str,
             'primary_index': True},
            {'name': 'st13',
             'type': str,
             'primary_index': False}
        ]
    ]
    }


PYPERS_TRIGGER = {
    'name': 'gbd_trigger',
    'indexes': [
        [
            {'name': 'name',
             'type': str,
             'primary_index': True},
        ]
    ]
}

PYPERS_OPERATIONS = {
    'name': 'gbd_daily_operation',
    'indexes': [
        [
            {'name': 'run_id',
             'type': str,
             'primary_index': True},
            {'name': 'collection',
             'type': str,
             'primary_index': False},
        ]
    ],
    'ttl': 3  # in days
}



PYPERS_ENTITY = {
    'name': 'gbd_pypers_entity',
    'indexes': [
        [
            {'name': 'entity_id',
             'type': str,
             'primary_index': True}
        ],
    ]
}
