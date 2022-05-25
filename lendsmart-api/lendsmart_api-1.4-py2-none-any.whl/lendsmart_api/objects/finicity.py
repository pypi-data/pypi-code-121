from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class FinicityReports(Base):
    """
    A Document is something a LendSmart customer uploads.
    """

    properties = {
        "customer_id": Property(identifier=True),
        "redirect_uri": Property(identifier=True),
        "voie_input": Property(mutable=True),
        "report_type": Property(mutable=True)         
    }


