import matplotlib as mpl
import wcag_contrast_ratio as cr


def score_contrast(a, b, large, AAA):
    contrast = cr.rgb(a, b)  # Between 1 and 21

    return contrast \
        + int((AAA and cr.passes_AAA(contrast, large=large))) * 100 \
        + int(not AAA and cr.passes_AA(contrast, large=large)) * 100


def best_color_contrast(bg_color, fg_colors, large=False, AAA=False):
    """
    Parameters
    ----------
    bg_color: string
        Background color in hexadecimal format.
    fg_colors: list of strings
        Foreground colors in hexadecimal format.
    large: bool
        Whether text is large. Large text is defined as 14 point (typically 18.66px) and bold or
        larger, or 18 point (typically 24px) or larger.
    AAA: bool
        Whether contrast ratio of at least 7:1 for normal text and 4.5:1 for large text is required.
        See https://www.w3.org/TR/WCAG20/#visual-audio-contrast

    Returns
    -------
    Text color in hexadecimal format.
    """
    bg_rgb = mpl.colors.to_rgb(bg_color)
    scores = [score_contrast(bg_rgb, mpl.colors.to_rgb(x), large, AAA) for x in fg_colors]

    return fg_colors[scores.index(max(scores))]
