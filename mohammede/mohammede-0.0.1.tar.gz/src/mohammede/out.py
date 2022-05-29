class Entry:
    def open(no=None,s=bool):
        if s == True:
            import pandas as pd
            from pywebio.output import put_html,put_file,put_button
            from pywebio import start_server
            import tkinter as tk
            from tkinter.filedialog import askopenfile
            def s():
                window = tk.Tk()

                file = askopenfile(filetypes=[('csv Files', '*.csv')])
                pdf_file = open(file.name, 'rb')

                s = pd.read_csv(pdf_file)
                h = open('dsf.html', 'w')
                e = s.to_html(h)
                h.close()
                put_html(e)

                se = open('dsf.html', 'rb').read()
                put_file('dsf.html', se, 'dsf.html')
                window.destroy()

            def o():
                put_button(label='dsf', onclick=s)

            start_server(o, debug=True)

