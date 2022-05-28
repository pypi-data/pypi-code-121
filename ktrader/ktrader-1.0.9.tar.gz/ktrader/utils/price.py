def round_px(px):
    if px == 0:
        return px
    px_0_0001 = 0.0001 * px
    if px_0_0001 < 1:
        ndigits = len(str(int(1 / px_0_0001)))
        px_round = round(px, ndigits)
    else:
        px_round = round(px, 1)
    if abs((px_round - px) / px) >= 0.0001:
        raise Exception(
            'px_round={px_round},px={px}'.format(
                px_round=px_round,
                px=px
            )
        )
    else:
        return px_round
