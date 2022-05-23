from cardtrader.service import CardTrader


def test_products_by_expansion(session: CardTrader):
    results = session.products_by_expansion(expansion_id=1)
    result = [x for x in results if x.id_ == 103811027]
    assert len(result) == 1
    assert result[0].quantity == 1
    assert result[0].description == "FRESH STOCK"
    assert result[0].blueprint_id == 9
    assert result[0].expansion is not None
    assert result[0].graded is False
    assert result[0].id_ == 103811027
    assert result[0].tag is None
    assert result[0].bundle_size == 1
    assert result[0].on_vacation is False
    assert result[0].seller is not None
    assert result[0].name == "Zahid, Djinn of the Lamp"
    assert result[0].price is not None
    assert result[0].properties is not None


def test_products_by_blueprint(session: CardTrader):
    results = session.products_by_blueprint(blueprint_id=1)
    result = [x for x in results if x.id_ == 127886155]
    assert len(result) == 1
    assert result[0].quantity == 1
    assert result[0].description == "TBS #1"
    assert result[0].blueprint_id == 1
    assert result[0].expansion is not None
    assert result[0].graded is False
    assert result[0].id_ == 127886155
    assert result[0].tag is None
    assert result[0].bundle_size == 1
    assert result[0].on_vacation is False
    assert result[0].seller is not None
    assert result[0].name == "Rampaging Brontodon"
    assert result[0].price is not None
    assert result[0].properties is not None
