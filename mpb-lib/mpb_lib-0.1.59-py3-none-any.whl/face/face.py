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


def load_script():
    html_body = HTML_fook(LOAD_SCRIPT)
    display_hook(html_body)


from .face_html import HTML_FRAME, WORD, STYLES, SCRIPT

HTML_TEMPLATE = """
${style}
${frame}
${word}
${script}
<script>
${functions}
</script>
"""

class Face:
    """
    JupyterやColaboratoryの出力セルに，助手さんの顔を表示するためのクラス。
    """
    CENTER = 152
    EYEBLOW_POS = (52, 180)
    EYE_POS = (52, 220)
    MOUTH_POS = (142, 305)

    def __init__(self):
        """
        オブジェクトの初期化
        """
        self.message = ""
        self.eyeblow_position = [0, 0]
        self.eyeblow_degree = 0
        self.eye_position = [0, 0]
        self.eye_kind = 0
        self.mouth_position = [0, 0]
        self.mouth_kind = 0


    def show(self):
        """
        顔を表示する。
        """
        html_source = Template(HTML_TEMPLATE)
        args = {"style": STYLES, "frame": HTML_FRAME,
                "script": SCRIPT, "functions": "",
                "word": ""}
        fcs = ""
        if self.message:
            args["word"] = WORD
            fcs = f"say('{self.message}');"
        if self.eye_kind in [0, 1, 2]:
            fcs += f"setBackground('left_eye', 'eye_l_{self.eye_kind+1}.png');"
            fcs += f"setBackground('right_eye', 'eye_r_{self.eye_kind+1}.png');"
        if self.mouth_kind in [0, 1, 2]:
            fcs += f"setBackground('mouth', 'mouth_{self.mouth_kind+1}.png');"

        if self.eye_position != [0, 0]:
            fcs += f"setXPosition('left_eye', {self.CENTER-self.EYE_POS[0]+self.eye_position[0]});"
            fcs += f"setYPosition('left_eye', {self.EYE_POS[1]+self.eye_position[1]});"
            fcs += f"setXPosition('right_eye', {self.CENTER+self.EYE_POS[0]-self.eye_position[0]});"
            fcs += f"setYPosition('right_eye', {self.EYE_POS[1]+self.eye_position[1]});"

        if self.eyeblow_position != [0, 0]:
            fcs += f"setXPosition('left_eyeblow', {self.CENTER-self.EYEBLOW_POS[0]+self.eyeblow_position[0]});"
            fcs += f"setYPosition('left_eyeblow', {self.EYEBLOW_POS[1]+self.eyeblow_position[1]});"
            fcs += f"setXPosition('right_eyeblow', {self.CENTER+self.EYEBLOW_POS[0]-self.eyeblow_position[0]});"
            fcs += f"setYPosition('right_eyeblow', {self.EYEBLOW_POS[1]+self.eyeblow_position[1]});"

        if self.eyeblow_degree:
            fcs += f"rotate('left_eyeblow', {self.eyeblow_degree});"
            fcs += f"rotate('right_eyeblow', {-self.eyeblow_degree});"

        if self.mouth_position != [0, 0]:
            fcs += f"setXPosition('mouth', {self.MOUTH_POS[0]+self.mouth_position[0]});"
            fcs += f"setYPosition('mouth', {self.MOUTH_POS[1]+self.mouth_position[1]});"


        args["functions"] = fcs

        html_body = HTML_fook(html_source.substitute(**args))
        display_hook(html_body)


    def say(self, message):
        """
        顔にセリフを追加する。
        """
        self.message = message
        self.show()
        self.message = ""
    
