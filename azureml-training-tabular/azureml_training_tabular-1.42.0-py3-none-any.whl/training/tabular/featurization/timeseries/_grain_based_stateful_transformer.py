# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base objects for Transformers and Estimators."""

from sklearn.base import TransformerMixin


class _GrainBasedStatefulTransformer(TransformerMixin):
    """Defines transformers which maintain per grain state."""

    pass
