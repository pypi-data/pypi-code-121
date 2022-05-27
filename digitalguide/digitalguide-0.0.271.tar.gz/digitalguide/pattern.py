
import re

# flags (iOS)
# symbols & pictographs
# emoticons
# transport & map symbols
# alchemical symbols
# Geometric Shapes Extended
# Supplemental Arrows-C
# Supplemental Symbols and Pictographs
# Chess Symbols
# Symbols and Pictographs Extended-A
# Dingbats
EMOJI_PATTERN = r"["\
    r"\U0001F1E0-\U0001F1FF"\
    r"\U0001F300-\U0001F5FF"\
    r"\U0001F600-\U0001F64F"\
    r"\U0001F680-\U0001F6FF"\
    r"\U0001F700-\U0001F77F"\
    r"\U0001F780-\U0001F7FF"\
    r"\U0001F800-\U0001F8FF"\
    r"\U0001F900-\U0001F9FF"\
    r"\U0001FA00-\U0001FA6F"\
    r"\U0001FA70-\U0001FAFF"\
    r"\U00002702-\U000027B0"\
    r"\U000024C2-\U0001F251"\
    r"]+"

JAHRESZAHL_PATTERN = r"(?P<jahreszahl>\d{1,4})"

KOMMAZAHL_PATTERN = r"(?P<vorkomma>\d+),? ?(?P<nachkomma>\d*)"

ZURUECK_PATTERN = "^("\
    "zurueck|"\
    "zurück"\
    ")$"\

WEITER_PATTERN ="^("\
    "gefunden|"\
    "bescheid|"\
    "weiter|"\
    "next|"\
    "nächster|"\
    "weit|"\
    "witer|"\
    "weitr|"\
    "überspringen|"\
    "uberspringen|"\
    "ueberspringen|"\
    "ueber springen|"\
    "waiter|"\
    "bin soweit|"\
    ")$"

WOHIN_PATTERN = "^("\
    "wohin|"\
    "wo|"\
    "weg|"\
    "wo lang|"\
    "route|"\
    "ziel|"\
    "ort|"\
    "woin|"\
    "treffpunkt|"\
    "GPS|"\
    "way|"\
    "where|"\
    "location|"\
    "Hilfe|"\
    "hilfe|"\
    "wie|"\
    "Wie"\
    ")$"

JA_PATTERN = "^("\
    "Okay|"\
    "ok|"\
    "okay|"\
    "OK|"\
    "Ok|"\
    "ja|"\
    "Ja|"\
    "Jap|"\
    "Jo|"\
    "Joa|"\
    "Yo|"\
    "Yap|"\
    "Yes|"\
    "Yess|"\
    "Yesss|"\
    "Jawohl|"\
    "jawol|"\
    "Jawoll|"\
    "Auf jeden Fall|"\
    "Auf jeden|"\
    "Klar|"\
    "Klaro|"\
    "Ci|"\
    "Cí|"\
    "Okay|"\
    "Ok|"\
    "Oki|"\
    "kay|"\
    "jes|"\
    "jep|"\
    "yep|"\
    "yop|"\
    "yup|"\
    "yupp|"\
    "Bin dabei|"\
    "dabie|"\
    "Gefunden|"\
    "bin da|"\
    "bin hier|"\
    "da|"\
    "hier|"\
    "angekommen|"\
    "geschafft|"\
    "fertig|"\
    "done|"\
    "👍|"\
    "👌|"\
    "🤚|"\
    "💪|"\
    "of course|"\
    "made it|"\
    "here|"\
    "found it|"\
    "bereit|"\
    "breit|"\
    "bin bereit|"\
    "ready|"\
    "readi|"\
    "redy|"\
    "kann losgehen|"\
    "kan losgehen|"\
    "okey|"\
    "oke|"\
    "abgemacht|"\
    "einverstanden|"\
    "ein verstanden|"\
    "gut|"\
    "gud|"\
    "jut|"\
    "ordnungsgemäß|"\
    "gebongt|"\
    "gecheckt|"\
    "gescheckt|"\
    "gechekt|"\
    "ist geritzt|"\
    "is geritzt|"\
    "all right|"\
    "allright|"\
    "d'accord|"\
    "daccord|"\
    "find ich gut|"\
    "find ich super|"\
    "sicher|"\
    "sure|"\
    "freilich|"\
    "freili|"\
    "logo|"\
    "logen|"\
    "na logo|"\
    "natürlich|"\
    "türlich|"\
    "tuerlich|"\
    "natuerlich|"\
    "immer|"\
    "alle Mal|"\
    "allemal|"\
    "gewiss|"\
    "gewiß|"\
    "gewis|"\
    "fraglos|"\
    "wahrlich|"\
    "warlich|"\
    "ausreichend|"\
    "zweifellos|"\
    "allerdings|"\
    "mit Sicherheit|"\
    "topp|"\
    "top|"\
    "oki doki|"\
    "okidoki|"\
    "von mir aus|"\
    "meinetwegen|"\
    "meinet wegen|"\
    "wenns sein muss|"\
    "wenn’s sein muss|"\
    "wens sein muss|"\
    "wen’s sein muss|"\
    "vermutlich|"\
    "wahrscheinlich|"\
    "glaube schon|"\
    "glaub schon|"\
    "bestimmt|"\
    "in der Tat|"\
    "positiv|"\
    ")$"

NEIN_PATTERN = "^("\
    "Nein|"\
    "nein|"\
    "Nope|"\
    "nop|"\
    "Nee|"\
    "ne|"\
    "neee|"\
    "nain|"\
    "nö|"\
    "auf keinen Fall|"\
    "auf keinsten|"\
    "no|"\
    "nada|"\
    "nien|"\
    "nicht|"\
    "never|"\
    "👎|"\
    "🙅‍♀️|"\
    "🙅‍♂️|"\
    "nimmermehr|"\
    "negativ|"\
    "veto|"\
    "weto|"\
    "keinesfalls|"\
    "nie und nimmer|"\
    "nieundnimmer|"\
    "sicher nicht|"\
    "unmöglich|"\
    "i wo|"\
    "mitnichten|"\
    "keineswegs|"\
    "gar nicht|"\
    ")$"