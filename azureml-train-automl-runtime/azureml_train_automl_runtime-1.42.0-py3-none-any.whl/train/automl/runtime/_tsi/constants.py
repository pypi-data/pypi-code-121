# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
TSI_COLUMN_PREFIX = "TSI_SYSTEM_DEFINED_"


class MLFlowInputColumns:
    Y_CONTEXT_COL = TSI_COLUMN_PREFIX + "Y_CONTEXT"
    Y_TEST_COL = TSI_COLUMN_PREFIX + "Y_TEST"


class MLFlowOutputColumns:
    Y_PRED_COL = TSI_COLUMN_PREFIX + "Y_PRED"
    Y_PRED_INV_TRANSFORMED_COL = TSI_COLUMN_PREFIX + "Y_PRED_INV_TRANSFORMED"
    Y_TEST_TRANSFORMED_COL = TSI_COLUMN_PREFIX + "Y_TEST_TRANSFORMED"


class PredictionFileConstants:
    OUTPUT_FILE_NAME_TEMPLATE = "predictions{}.csv"
    ORIGINAL_COL_SUFFIX = "_orig"
    PREDICTED_COL_SUFFIX = "_predicted"
    PREDICTED_PROBA_COL_SUFFIX = "_predicted_proba"
