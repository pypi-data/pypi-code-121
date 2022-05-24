# -*- coding: utf-8 -*-
"""
Functional specification for the bowyer.cfg.validate module.

"""


import pytest


# =============================================================================
class SpecifyNormalized:
    """
    Spec for the normalized validation function.

    """

    # -------------------------------------------------------------------------
    def it_accepts_valid_data(self, valid_normalized_config):
        """
        Check normalized does not throw when given valid data.

        """
        import bowyer.cfg.validate  # pylint: disable=C0415

        bowyer.cfg.validate.normalized(valid_normalized_config)

    # -------------------------------------------------------------------------
    def it_rejects_invalid_data(self, invalid_config):
        """
        Check normalized raises an exception when given invalid data.

        """
        import bowyer.cfg.exception  # pylint: disable=C0415
        import bowyer.cfg.validate   # pylint: disable=C0415

        with pytest.raises(bowyer.cfg.exception.CfgError):
            bowyer.cfg.validate.normalized(invalid_config)


# =============================================================================
class SpecifyDenormalized:
    """
    Spec for the denormalized validation function.

    """

    # -------------------------------------------------------------------------
    def it_accepts_valid_data(self, valid_normalized_config):
        """
        Check normalized does not throw when given valid data.

        """
        import bowyer.cfg           # pylint: disable=C0415
        import bowyer.cfg.validate  # pylint: disable=C0415

        valid_denormalized_config = bowyer.cfg.denormalize(
                                                    valid_normalized_config)
        bowyer.cfg.validate.denormalized(valid_denormalized_config)

    # -------------------------------------------------------------------------
    def it_rejects_invalid_data(self, invalid_config):
        """
        Check normalized raises an exception when given invalid data.

        """
        import bowyer.cfg.exception  # pylint: disable=C0415
        import bowyer.cfg.validate   # pylint: disable=C0415

        with pytest.raises(bowyer.cfg.exception.CfgError):
            bowyer.cfg.validate.denormalized(invalid_config)
