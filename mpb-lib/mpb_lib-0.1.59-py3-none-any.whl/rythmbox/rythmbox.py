from string import Template

from IPython.display import display, HTML
try:
    from google.colab.output import eval_js
except:
    def eval_js(js):
        body = HTML(f"""<script>
        {js}
        </script>""")
        display(body)

from .rythmbox_html import (JAVASCRIPT, HEAD,
            HTML_FRAME, COL_TEMPLATE, MCOL_TEMPLATE, ROW_TEMPLATE)

colors = ["red", "yellow", "green", "blue",
          "lime", "purple", "orange"]

display(HTML(HEAD))

def make_cols(an_id, klass, cols, data, tmpl):
    col_html = ""
    for i in range(cols):
        t = Template(tmpl)
        k_addition = ""
        if i in data:
            k_addition = " on"
        part = t.substitute(**{"an_id":an_id, "klass":klass+k_addition, "pos":i})
        col_html += part
    return col_html


def show_frame(data, cols, rows=1):
    display(HTML(HEAD))

    rt = Template(ROW_TEMPLATE)

    # インジケーターを作る
    col_html = make_cols("i", "indicator", cols, [], MCOL_TEMPLATE)
    mk_html = rt.substitute(**{"cols":col_html})

    # ブロックを作る
    bl_html = ""
    for r in range(rows):
        col_html = make_cols("g", "button "+colors[r], cols, data[r], COL_TEMPLATE)
        bl_html += rt.substitute(**{"cols":col_html})

    jst = Template(JAVASCRIPT)
    js = jst.substitute(**{"speed":250, "cols": cols})

    frame = Template(HTML_FRAME)
    args = {"script":js, "markers":mk_html,
            "blocks":bl_html, "cols": cols}
    display(HTML(frame.substitute(**args)))


def rb(timings):
    if isinstance(timings, list):
        if isinstance(timings[0], int):
            timing_list = [x for x in timings if x < 8]
            show_frame([timing_list], 8)
        elif isinstance(timings[0], str):
            timing_list = [[], [], [], []]
            for ti, ts in enumerate(timings):
                for i, s in enumerate(ts):
                    if s == "1":
                        timing_list[ti].append(i)
            show_frame(timing_list, 8, 4)

    elif isinstance(timings, str):
        timing_list = [n for n, x in enumerate(timings[:8]) if x == "1"]
        show_frame([timing_list], 8)


def rb2(timing_str_list):
    timing_str = timing_str_list[:8]
    timings = [[], [], [], []]
    for i in range(0, len(timing_str)):
        for n, s in enumerate(words):
            if s in timing_str[i].lower():
                timings[n].append(i)
    show_frame(timings, 8, 4)


    
