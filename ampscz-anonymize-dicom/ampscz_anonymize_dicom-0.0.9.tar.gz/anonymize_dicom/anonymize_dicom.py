# -*- coding: utf-8 -*-
from threading import Thread
import shutil
import time
import re
import pydicom
from pathlib import Path
import os
import platform
from tkinter import messagebox
from tkinterdnd2 import *
import tempfile as tf
try:
    from Tkinter import *
    from ScrolledText import ScrolledText
except ImportError:
    from tkinter import *
    from tkinter.scrolledtext import ScrolledText

from tkinter import ttk


def anonymize_dicom():
    root = TkinterDnD.Tk()
    root.withdraw()
    root.title('AMP-SCZ dicom deidentification tool')
    root.grid_rowconfigure(1, weight=1, minsize=100)
    root.grid_rowconfigure(2, weight=1, minsize=10)
    root.grid_rowconfigure(3, weight=1, minsize=100)
    root.grid_rowconfigure(4, weight=1, minsize=10)
    root.grid_rowconfigure(5, weight=1, minsize=50)

    root.grid_columnconfigure(0, weight=1, minsize=300)
    root.grid_columnconfigure(1, weight=1, minsize=300)
    root.grid_columnconfigure(2, weight=1, minsize=300)
    root.grid_columnconfigure(3, weight=1, minsize=20)
    root.grid_columnconfigure(4, weight=1, minsize=20)


    def print_event_info(event):
        print('\nAction:', event.action)
        print('Supported actions:', event.actions)
        print('Mouse button:', event.button)
        print('Type codes:', event.codes)
        print('Current type code:', event.code)
        print('Common source types:', event.commonsourcetypes)
        print('Common target types:', event.commontargettypes)
        print('Data:', event.data)
        print('Event name:', event.name)
        print('Supported types:', event.types)
        print('Modifier keys:', event.modifiers)
        print('Supported source types:', event.supportedsourcetypes)
        print('Operation type:', event.type)
        print('Source types:', event.sourcetypes)
        print('Supported target types:', event.supportedtargettypes)
        print('Widget:', event.widget, '(type: %s)' % type(event.widget))
        print('X:', event.x_root)
        print('Y:', event.y_root, '\n')


    def check_name(name):
        if re.match('[A-Z]{2}\d{5}', name):
            name_check = True
        else:
            name_check = False
            messagebox.showwarning(
                    title='Please check AMP-SCZ subject ID',
                    message='Please check AMP-SCZ subject ID. It should have '
                    'two letters, followed by five digits. eg) ME00001')
        return name_check


    def check_dirs(dicom_root, output_dir):
        if dicom_root.is_dir() and output_dir.is_dir():
            dicom_root_check = True
        else:
            dicom_root_check = False
            messagebox.showwarning(
                    title='Incorrect dicom folder path',
                    message='Please check if the dicom folder path exists')
            listbox.delete(0, END)
            outbox.delete(0, END)

        return dicom_root_check

    def run_deidentification():

        button['state'] = "disabled"
        name = text.get()
        session = session_text.get()
        dicom_root = Path(listbox.get(0))  # get first item
        output_dir = Path(outbox.get(0))

        name_check = check_name(name)
        dicom_root_check = check_dirs(dicom_root, output_dir)

        vars = ['AccessionNumber',
                'ReferringPhysicianName',
                'PerformingPhysicianName',
                'PatientName',
                'PatientID',
                'PatientBirthDate',
                'PerformedProcedureStepDescription',
                'InstitutionalDepartmentName',
                'InstitutionName',
                'InstitutionAddress']
        fill_in_infor(dicom_root, name, session, vars)
        root.update_idletasks()

        time.sleep(1)
        yes = messagebox.askyesno(
                title='Following information will be removed',
                message="\n".join(vars))

        if yes:
            t = Thread(target=get_dicom_info,
                       args=(dicom_root, name, session, output_dir, vars))
            t.start()


    def fill_in_infor(dicom_root, name, session, vars):
        data_dict = {}
        for roott, dirs, files in os.walk(dicom_root):
            for file in files:
                f = pydicom.read_file(Path(roott) / file, force=True)
                for var in vars:
                    if var == 'PatientName':
                        replace_val = name
                    elif var == 'PatientID':
                        replace_val = session
                    elif var == 'PatientBirthDate':
                        replace_val = '19000101'
                    else:
                        replace_val = 'deidentified'

                    try:
                        data_dict[var] = getattr(f, var)
                        before_header_box.insert(END,
                                f"{var}: {data_dict[var]}")

                        after_header_box.insert(END,
                                f"{var}: {replace_val}")
                        date_row = f.AcquisitionDate
                        root.update_idletasks()
                    except:
                        pass
                return


    def get_dicom_info(dicom_root: Path, name, session, output_dir, vars):
        dicoms = 0
        for roott, dirs, files in os.walk(dicom_root):
            for file in files:
                dicoms += 1

        progress['maximum'] = dicoms * 1.5

        tmpdirname = tf.mkdtemp()
        k = 0
        for roott, dirs, files in os.walk(dicom_root):
            for file in files:
                f = pydicom.read_file(Path(roott) / file, force=True)
                new_file_loc = re.sub(str(dicom_root),
                        tmpdirname,
                        str(Path(roott) / file))
                Path(new_file_loc).parent.mkdir(exist_ok=True, parents=True)
                for var in vars:
                    if var == 'PatientName':
                        replace_val = name
                    elif var == 'PatientID':
                        replace_val = session
                    else:
                        replace_val = 'deidentified'
                    setattr(f, var, replace_val)
                f.save_as(new_file_loc)
                progress['value'] = k
                k += 1
                root.update_idletasks()

        a = Label(root, text='**Zipping the file**')
        a.grid(row=5, column=2, padx=50, pady=5)
        date_row = f.AcquisitionDate
        year = date_row[:4]
        month = date_row[4:6]
        day = date_row[6:]
        out_zip_loc = Path(output_dir) / \
                f"{name}_MR_{year}_{month}_{day}_{session}"

        t = Thread(target=shutil.make_archive,
                   args=(out_zip_loc, 'zip', tmpdirname))
        t.start()
        while t.is_alive():
            progress['value'] += 1
            time.sleep(0.5)

        t.join()
        progress['value'] = dicoms * 1.5
        a.destroy()

        shutil.rmtree(tmpdirname)

        messagebox.showinfo(
                title='Done',
                message='Please upload the zip file to the mediaflux\n'
                        f'{out_zip_loc}.zip')

        button['state'] = "normal"
        return


    Label(root, text='Drag and drop dicom folder here:').grid(
                        row=0, column=0, padx=10, pady=5)

    Label(root, text='Drag and drop output folder here:').grid(
                        row=2, column=0, padx=10, pady=5)

    Label(root, text='Enter AMP-SCZ subject ID:').grid(
                        row=0, column=1, padx=10, pady=5)

    Label(root, text='Enter Session number:').grid(
                        row=2, column=1, padx=10, pady=5)

    Label(root, text='Information before deidentification:').grid(
                        row=0, column=2, padx=50, pady=5)

    Label(root, text='Information after deidentification:').grid(
                        row=2, column=2, padx=50, pady=5)

    buttonbox = Frame(root)
    buttonbox.grid(row=5, column=0, columnspan=2, pady=5)
    # Button(buttonbox, text='Run deidentification',
            # command=root.quit).pack(
                        # side=LEFT, padx=5)
    button = Button(buttonbox, text='Run deidentification',
            command=run_deidentification).pack(side=LEFT, padx=5)


    ##############################################################################
    ######   Basic demo window: a Listbox to drag & drop files                  ##
    ######   and a Text widget to drag & drop text                              ##
    ##############################################################################
    listbox = Listbox(root, name='dnd_demo_listbox',
                        selectmode='extended', width=1, height=1)
    listbox.grid(row=1, column=0, padx=5, pady=5, sticky='news')
    # listbox.insert(END, '')

    outbox = Listbox(root, name='dnd_demo_outbox',
                        selectmode='extended', width=1, height=1)
    outbox.grid(row=3, rowspan=2, column=0, padx=5, pady=5, sticky='news')
    # outbox.insert(END, '')

    before_header_box = Listbox(
            root, name='dnd_demo_before',
            selectmode='extended', width=1, height=1)
    before_header_box.grid(row=1, column=2, rowspan=1, columnspan=2, padx=5, pady=5, sticky='news')

    after_header_box = Listbox(
            root, name='dnd_demo_after',
            selectmode='extended', width=1, height=1)
    after_header_box.grid(row=3, column=2, rowspan=2, columnspan=2, padx=5, pady=5, sticky='news')

    # text = Text(root, name='dnd_demo_text', wrap='word', undo=True, width=1, height=1)
    text = Entry(root, name='dnd_demo_text', width=1)
    text.grid(row=1, column=1, pady=5, sticky='news')
    text.insert(END, 'ME00000')

    session_text = Entry(root, name='dnd_demo_ha', width=1)
    session_text.grid(row=3, column=1, pady=5, rowspan=2, sticky='news')
    session_text.insert(END, 1)


    progress = ttk.Progressbar(root, orient=VERTICAL,
                               mode='determinate')
    progress.grid(row=1, column=4, pady=5, rowspan=4, sticky='news')




    # Drop callbacks can be shared between the Listbox and Text;
    # according to the man page these callbacks must return an action type,
    # however they also seem to work without

    def drop_enter(event):
        event.widget.focus_force()
        # print('Entering widget: %s' % event.widget)
        #print_event_info(event)
        return event.action

    def drop_position(event):
        # print('Position: x %d, y %d' %(event.x_root, event.y_root))
        #print_event_info(event)
        return event.action

    def drop_leave(event):
        # print('Leaving %s' % event.widget)
        #print_event_info(event)
        # print(text.pack())
        return event.action

    def drop(event):
        if event.data:
            print('Root of dicom directory:\n', event.data)
            #print_event_info(event)
            if event.widget == listbox:
                # event.data is a list of filenames as one string;
                # if one of these filenames contains whitespace characters
                # it is rather difficult to reliably tell where one filename
                # ends and the next begins; the best bet appears to be
                # to count on tkdnd's and tkinter's internal magic to handle
                # such cases correctly; the following seems to work well
                # at least with Windows and Gtk/X11
                files = listbox.tk.splitlist(event.data)
                for f in files:
                    if os.path.exists(f):
                        # print('Dropped file: "%s"' % f)
                        listbox.insert('end', f)
                    else:
                        print('Not dropping file "%s": file does not exist.' % f)

            elif event.widget == text:
                # calculate the mouse pointer's text index
                bd = text['bd'] + text['highlightthickness']
                x = event.x_root - text.winfo_rootx() - bd
                y = event.y_root - text.winfo_rooty() - bd
                index = text.index('@%d,%d' % (x,y))
                text.insert(index, event.data)
            else:
                print('Error: reported event.widget not known')
        return event.action

    def drop_out(event):
        if event.data:
            print('Output directory to save the zip file:\n', event.data)
            #print_event_info(event)
            if event.widget == outbox:
                # event.data is a list of filenames as one string;
                # if one of these filenames contains whitespace characters
                # it is rather difficult to reliably tell where one filename
                # ends and the next begins; the best bet appears to be
                # to count on tkdnd's and tkinter's internal magic to handle
                # such cases correctly; the following seems to work well
                # at least with Windows and Gtk/X11
                files = outbox.tk.splitlist(event.data)
                for f in files:
                    if os.path.exists(f):
                        # print('Dropped file: "%s"' % f)
                        outbox.insert('end', f)
                    else:
                        print('Not dropping file "%s": file does not exist.' % f)

            elif event.widget == text:
                # calculate the mouse pointer's text index
                bd = text['bd'] + text['highlightthickness']
                x = event.x_root - text.winfo_rootx() - bd
                y = event.y_root - text.winfo_rooty() - bd
                index = text.index('@%d,%d' % (x,y))
                text.insert(index, event.data)
            else:
                print('Error: reported event.widget not known')
        return event.action

    # now make the Listbox and Text drop targets
    listbox.drop_target_register(DND_FILES, DND_TEXT)
    outbox.drop_target_register(DND_FILES, DND_TEXT)
    text.drop_target_register(DND_TEXT)

    for widget in (listbox, text):
        widget.dnd_bind('<<DropEnter>>', drop_enter)
        widget.dnd_bind('<<DropPosition>>', drop_position)
        widget.dnd_bind('<<DropLeave>>', drop_leave)
        widget.dnd_bind('<<Drop>>', drop)
        #widget.dnd_bind('<<Drop:DND_Files>>', drop)
        #widget.dnd_bind('<<Drop:DND_Text>>', drop)

    for widget in (outbox, text):
        widget.dnd_bind('<<DropEnter>>', drop_enter)
        widget.dnd_bind('<<DropPosition>>', drop_position)
        widget.dnd_bind('<<DropLeave>>', drop_leave)
        widget.dnd_bind('<<Drop>>', drop_out)
    # define drag callbacks

    def drag_init_listbox(event):
        print_event_info(event)
        # use a tuple as file list, this should hopefully be handled gracefully
        # by tkdnd and the drop targets like file managers or text editors
        data = ()
        if listbox.curselection():
            data = tuple([listbox.get(i) for i in listbox.curselection()])
            print('Dragging :', data)
        # tuples can also be used to specify possible alternatives for
        # action type and DnD type:
        return ((ASK, COPY), (DND_FILES, DND_TEXT), data)

    def drag_init_outbox(event):
        print_event_info(event)
        # use a tuple as file list, this should hopefully be handled gracefully
        # by tkdnd and the drop targets like file managers or text editors
        data = ()
        if outbox.curselection():
            data = tuple([outbox.get(i) for i in outbox.curselection()])
            print('Dragging :', data)
        # tuples can also be used to specify possible alternatives for
        # action type and DnD type:
        return ((ASK, COPY), (DND_FILES, DND_TEXT), data)

    def drag_init_text(event):
        print_event_info(event)
        # use a string if there is only a single text string to be dragged
        data = ''
        sel = text.tag_nextrange(SEL, '1.0')
        if sel:
            data = text.get(*sel)
            print('Dragging :\n', data)
        # if there is only one possible alternative for action and DnD type
        # we can also use strings here
        return (COPY, DND_TEXT, data)

    def drag_end(event):
        #print_event_info(event)
        # this callback is not really necessary if it doesn't do anything useful
        print('Drag ended for widget:', event.widget)


    # finally make the widgets a drag source
    listbox.drag_source_register(1, DND_TEXT, DND_FILES)
    text.drag_source_register(3, DND_TEXT)

    listbox.dnd_bind('<<DragInitCmd>>', drag_init_listbox)
    listbox.dnd_bind('<<DragEndCmd>>', drag_end)
    text.dnd_bind('<<DragInitCmd>>', drag_init_text)



    # outbox
    # finally make the widgets a drag source
    outbox.drag_source_register(1, DND_TEXT, DND_FILES)
    text.drag_source_register(3, DND_TEXT)

    outbox.dnd_bind('<<DragInitCmd>>', drag_init_outbox)
    outbox.dnd_bind('<<DragEndCmd>>', drag_end)
    text.dnd_bind('<<DragInitCmd>>', drag_init_text)

    # skip the useless drag_end() binding for the text widget

    root.update_idletasks()
    root.deiconify()
    root.mainloop()

if __name__ == '__main__':
    anonymize_dicom()
