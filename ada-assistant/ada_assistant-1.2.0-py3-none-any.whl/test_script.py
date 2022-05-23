import os
from ada import txt_editor
# editor = txt_editor.LineFixedTxtEditor(100, ["hello"*100, "world"])
# print(editor.run())

_, EDITOR_WIDTH = os.popen('stty size', 'r').read().split()
editor = txt_editor.LineFixedTxtEditor(int(EDITOR_WIDTH) - 1, ["helllo "*3, "worrrld"], ["1:", "222222:"])
print(editor.run())

# editor = txt_editor.InteractivePrompt(100, "yes or no: ")
# print(editor.run())
