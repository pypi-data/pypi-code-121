class PredictionTypeConstants:
    VERY_HIGH = 2
    HIGH = 1
    FLAT = 0
    LOW = -1
    VERY_LOW = -2


class ITrader:
    """
    least functionality that live model runner needs
    """

    def predict_market(self, data) -> PredictionTypeConstants:
        """

        Returns
        -------
        POSITION_LONG or POSITION_NONE, POSITION_SHORT
        """
        pass


class ITraderFactory:
    def create_trader(self) -> ITrader:
        """
        Create a Trader

        """
        pass
