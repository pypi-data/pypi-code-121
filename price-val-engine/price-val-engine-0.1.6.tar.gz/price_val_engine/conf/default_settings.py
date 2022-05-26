import os
# inlude validation pipeline here

# EMPTY VALUES configuration

EMPTY_VALUES = (None, "", [], (), {})

# General Validation Out of range configuration

GEN_VAL_OUT_OF_RANGE_VALUE = {
  'min_value': 100000.0,
  'max_value': 10000000.0
}

# Validation Pipelies
VALIDATION_PIPELINES = [
  'price_val_engine.core.validations.general_rules.NullNegativeZeroValidationRule',
  'price_val_engine.core.validations.general_rules.OutOfRangeValidationRule',
  'price_val_engine.core.validations.revision_rules.DeltaPercentageFromLastDayRule',
]

# AWS CONFIGRATION
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN     = os.environ.get('AWS_SESSION_TOKEN')

# google cloud CONFIGRATION
GCS_TOKEN = os.environ.get('GCS_TOKEN', 'anon')


# NOTIFICATION ALEERT
SLACK_ENABLED = False
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
