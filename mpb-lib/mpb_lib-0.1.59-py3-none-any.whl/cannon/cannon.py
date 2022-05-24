from string import Template
from random import randint
from math import floor

from IPython.display import display, HTML
try:
    from google.colab.output import eval_js
    HTML_fook = HTML
    display_hook = display


except:
    from IPython.display import IFrame
    from IPython.display import FileLink
    def eval_js(js):
        body = HTML(f"""<script>
        {js}
        </script>""")
        display(body)


    def HTML_fook(body):
        f = open('./tmp.html', 'w')
        f.write(body)
        f.close()


    def display_hook(html):
        display(IFrame('./tmp.html', width="100%", height="400px"))

DELTA = 0

def set_delta():
    global DELTA
    while not DELTA:
        DELTA = randint(-5, 5)*5


def load_script():
    html_body = HTML_fook(LOAD_SCRIPT)
    display_hook(html_body)


from .cannon_html import HTML_TEMPLATE, SCRIPT, LOAD_SCRIPT

def cannon_game(powder):
    html_source = Template(HTML_TEMPLATE)
    args = {"SCRIPT":SCRIPT, "stage":1, "powder":powder, "delta": 0,
            "dist_display": ""}
    html_body = HTML_fook(html_source.substitute(**args))
    display_hook(html_body)


def cannon_game2(powder):
    html_source = Template(HTML_TEMPLATE)
    args = {"SCRIPT":SCRIPT, "stage":2, "powder":powder, "delta": 0,
            "dist_display": ""}
    html_body = HTML_fook(html_source.substitute(**args))
    display_hook(html_body)


def cannon_game3(powder, delta=-1):
    global DELTA
    if delta != -1:
        DELTA = delta
    else:
        set_delta()
    html_source = Template(HTML_TEMPLATE)
    args = {"SCRIPT":SCRIPT, "stage":2, "powder":powder, "delta": DELTA,
            "dist_display": "距離 : "+str(450+DELTA)}
    html_body = HTML_fook(html_source.substitute(**args))
    display_hook(html_body)

    DELTA = 0


def get_distance():
    set_delta()
    return DELTA+450


def calc_powder(distance):
    p = ((50*(distance+10))/(9*2.643))**0.5
    return floor(p*1000)/1000
