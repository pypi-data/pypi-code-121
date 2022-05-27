import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle


def plot_ohlc_candles(ohlc, shrink_factor=0.75):
    interval_size = ohlc.index.values[1] - ohlc.index.values[0]

    ax = plt.gca()
    for b, row in ohlc.iterrows():
        if row['open'] < row['close']:
            color = 'green'
        else:
            color = 'red'

        # candle bodies
        rectangle = Rectangle(
            (b, min(row['open'], row['close'])),
            interval_size * shrink_factor,
            abs(row['open'] - row['close']),
            color=color,
        )
        ax.add_patch(rectangle)

        # candle wicks
        b_half = b + interval_size * shrink_factor / 2
        top = max(row['open'], row['close'])
        bottom = min(row['open'], row['close'])
        plt.plot([b_half, b_half], [top, row['high']], color=color)
        plt.plot([b_half, b_half], [bottom, row['low']], color=color)


def plot_ohlc_candles_raw_overlay(values, indices, alpha=0.3):
    plt.plot(indices, values, '.k', markersize=10, zorder=99, alpha=alpha)
    plt.plot(indices, values, '-k', zorder=99, linewidth=1, alpha=alpha)


def plot_ohlc_as_lines(ohlc):
    for item in ['open', 'high', 'low', 'close']:
        plt.plot(ohlc[item], '.-', label=item, linewidth=0.5)

