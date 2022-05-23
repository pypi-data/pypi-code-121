import readtime
import math

READING_RATE = 100 # words per minute
# What is a sensible reading rate for undergraduate level academic teaching material?
# 250 wpm gives a rate of 15,000 wph
# 10,000 wph corresponds to about 170 words per minute
# OU guidance: 35 wpm for challenging texts, 70 wpm for medium texts, 120 wpm for easy texts

def md_readtime(md, reading_rate=READING_RATE, rounding_override=False, rounded_minutes=False, **kwargs):
    """Get reading time in seconds."""
    rt = readtime.of_markdown(md, wpm=reading_rate).delta.total_seconds()

    #Round up on the conversion of estimated reading time in seconds, to minutes...
    #f'Reading time in seconds: {rt}; in minutes: {math.ceil(rt/60)}.'
    if not rounding_override and rounded_minutes:
        return math.ceil(rt/60)
    return rt