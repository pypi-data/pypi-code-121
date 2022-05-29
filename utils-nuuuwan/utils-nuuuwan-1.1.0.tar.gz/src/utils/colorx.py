import colorsys
import random

PRECISION = 2


def random_hsl_vector(hue=None, saturation=None, lightness=None):
    hue0 = round(random.random(), PRECISION)
    saturation0 = 1
    lightness0 = 0.8

    hue = hue0 if (hue is None) else hue
    saturation = saturation0 if (saturation is None) else saturation
    lightness = lightness0 if (lightness is None) else lightness

    return (hue, saturation, lightness)


def random_rgb_vector(red=None, green=None, blue=None):
    (hue, saturation, lightness) = random_hsl_vector()
    (red0, green0, blue0) = list(map(
        lambda x: (int)(x * 255),
        colorsys.hls_to_rgb(hue, lightness, saturation),
    ))

    red = red0 if (red is None) else red
    green = green0 if (green is None) else green
    blue = blue0 if (blue is None) else blue

    return (red, green, blue)


def random_hsl(hue=None, saturation=None, lightness=None):
    (hue, saturation, lightness) = random_hsl_vector(hue, saturation, lightness)
    return f'hsl({hue:.0f},{saturation:.0%},{lightness:.0%})'


def random_rgb(red=None, green=None, blue=None):
    (red, green, blue) = random_rgb_vector(red, green, blue)
    return f'rgb({red},{green},{blue})'


def random_hex(red=None, green=None, blue=None):
    (r, g, b) = random_rgb_vector(red, green, blue)
    return f'#{r:02x}{g:02x}{b:02x}'
