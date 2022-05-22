from cardtrader.service import CardTrader


def test_categories(session: CardTrader):
    results = session.categories()
    result = [x for x in results if x.id_ == 1]
    assert len(result) == 1
    assert result[0].id_ == 1
    assert result[0].name == "Magic Single Card"
    assert result[0].game_id == 1
    assert result[0].properties is not None


def test_categories_with_game_id(session: CardTrader):
    results = session.categories(game_id=6)
    result = [x for x in results if x.id_ == 80]
    assert len(result) == 1
    assert result[0].id_ == 80
    assert result[0].name == "Flesh and Blood Single Card"
    assert result[0].game_id == 6
    assert result[0].properties is not None
