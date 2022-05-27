import numpy as np
import pandas as pd
from numba import jit


@jit(nopython=True)
def combine_taggers(decs, omegas):
    # events with omega > 0.5 do not contribute with information in combinations
    for t, omega in enumerate(omegas):
        ignore = omega > 0.5
        omegas[t][ignore] = 0.5
        decs[t][ignore] = 0

    # Tagger combination algorithm
    NT = len(omegas)
    p_b    = np.array([np.prod((1 + decs[i]) / 2 - decs[i] * (1 - omegas[i])) for i in range(NT)])
    p_bbar = np.array([np.prod((1 - decs[i]) / 2 + decs[i] * (1 - omegas[i])) for i in range(NT)])

    P_b = p_b / (p_b + p_bbar)

    dec_minus = P_b > 1 - P_b
    dec_plus  = P_b < 1 - P_b

    d_combined = np.zeros(len(decs))
    d_combined[dec_minus] = -1
    d_combined[dec_plus]  = +1

    omega_combined = 0.5 * np.ones(len(decs))
    omega_combined[dec_minus] = 1 - P_b[dec_minus]
    omega_combined[dec_plus]  = P_b[dec_plus]

    return d_combined, omega_combined


def _correlation(taggers, corrtype="dec_weight", selected=True, calibrated=False):
    @jit(nopython=True)
    def corr(X, Y, W):
        Neff = np.sum(W)
        avg_X = np.sum(X * W) / Neff
        avg_Y = np.sum(Y * W) / Neff
        Xres = X - avg_X
        Yres = Y - avg_Y
        covXY = np.sum(W * Xres * Yres) / Neff
        covXX = np.sum(W * Xres * Xres) / Neff
        covYY = np.sum(W * Yres * Yres) / Neff
        return covXY / np.sqrt(covXX * covYY)

    N = len(taggers)
    m_corr = np.ones((N, N)) * -999  # If something is not filled, show -999

    class getter:
        def __init__(self, stats):
            self.stats = stats

        def __call__(self, tagger, attr):
            return np.array(getattr(getattr(tagger, self.stats)._full_data, attr)[getattr(tagger, self.stats)._full_data.selected])

    get = getter("cstats" if calibrated else "stats")

    for x, TX in enumerate(taggers):
        for y, TY in enumerate(taggers[x:]):
            if TX.name == TY.name:
                m_corr[x][x + y] = 1
                continue
            if calibrated:
                assert TY.is_calibrated()
            if corrtype == "fire":
                try:
                    m_corr[x][x + y] = corr(np.abs(get(TX, "dec")),
                                            np.abs(get(TY, "dec")),
                                            get(TX, "weight"))
                except ZeroDivisionError:
                    m_corr[x][x + y] = np.nan
            elif corrtype == "dec":
                m_corr[x][x + y] = corr(get(TX, "dec"),
                                        get(TY, "dec"),
                                        get(TX, "weight"))
            elif corrtype == "dec_weight":
                m_corr[x][x + y] = corr(get(TX, "dec") * (1 - 2 * get(TX, "eta")),
                                        get(TY, "dec") * (1 - 2 * get(TY, "eta")),
                                        get(TX, "weight"))
            elif corrtype == "both_fire":
                d1 = get(TX, "dec")
                d2 = get(TY, "dec")
                mask = (d1 != 0) & (d2 != 0)
                m_corr[x][x + y] = corr(d1[mask], d2[mask], get(TX, "weight")[mask])

            m_corr[x + y][x] = m_corr[x][x + y]

    names = [tagger.name for tagger in taggers]
    m_corr = pd.DataFrame({name : m_corr[n] for n, name in enumerate(names)}, index = names)
    return m_corr
