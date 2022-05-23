from cardtrader.service import CardTrader


def test_blueprints(session: CardTrader):
    results = session.blueprints(expansion_id=1)
    result = [x for x in results if x.id_ == 6]
    assert len(result) == 1
    assert result[0].id_ == 6
    assert result[0].name == "Ghalta, Primal Hunger"
    assert result[0].version is None
    assert result[0].game_id == 1
    assert result[0].category_id == 1
    assert result[0].expansion_id == 1
    assert (
        result[0].image_url == "https://cardtrader.com/uploads/blueprints/image/6"
        "/preview_gnt-44-ghalta-primal-hunger.jpg"
    )
    assert result[0].card_market_id == 366585
    assert result[0].tcg_player_id == 180397
    assert result[0].scryfall_id == "b2a93747-720a-4ddf-8325-36db78e0a584"
    assert result[0].fixed_properties is not None
    assert result[0].editable_properties is not None


def test_null_pricing(session: CardTrader):
    results = session.blueprints(expansion_id=2591)
    result = [x for x in results if x.id_ == 169160]
    assert len(result) == 1
    assert result[0].id_ == 169160
    assert result[0].card_market_id is None
    assert result[0].tcg_player_id is None
    assert result[0].scryfall_id is None
