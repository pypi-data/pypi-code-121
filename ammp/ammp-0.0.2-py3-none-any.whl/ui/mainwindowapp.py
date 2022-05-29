import tkinter as tk
import tkinter.ttk as ttk


class MainWindowApp:
    def __init__(self, master=None):
        # build ui
        self.frm_main_window = ttk.Frame(master)
        self.frm_menu = ttk.Frame(self.frm_main_window)
        self.frm_menu.configure(height='30', width='1024')
        self.frm_menu.grid(sticky='nsew')
        self.frm_menu.rowconfigure('0', minsize='30', uniform='None',
                                   weight='0')
        self.frm_menu.columnconfigure('0', minsize='0', uniform='None',
                                      weight='1')
        self.main_window = ttk.Panedwindow(self.frm_main_window,
                                           orient='horizontal')
        self.frm_manouver_list = ttk.Frame(self.main_window)
        self.manouver_list = ttk.Treeview(self.frm_manouver_list)
        self.manouver_list.grid(sticky='nsew')
        self.manouver_list.rowconfigure('0', weight='1')
        self.manouver_list.columnconfigure('0', weight='1')
        self.frm_manouver_list.configure(height='600', width='124')
        self.frm_manouver_list.grid(sticky='nsew')
        self.frm_manouver_list.rowconfigure('0', weight='1')
        self.frm_manouver_list.columnconfigure('0', weight='1')
        self.main_window.add(self.frm_manouver_list, weight='0')
        self.content_container_window = ttk.Panedwindow(self.main_window,
                                                        orient='vertical')
        self.content_window_top = ttk.Panedwindow(
            self.content_container_window, orient='horizontal')
        self.frm_map_view = ttk.Frame(self.content_window_top)
        self.frm_map_view_menu = ttk.Frame(self.frm_map_view)
        self.frm_map_view_menu.configure(height='30', width='200')
        self.frm_map_view_menu.grid(sticky='new')
        self.frm_map_view_menu.rowconfigure('0', weight='1')
        self.frm_map_view_menu.columnconfigure('0', weight='1')
        self.frm_map_view_content = ttk.Frame(self.frm_map_view)
        self.frm_map_view_content.configure(height='270', width='200')
        self.frm_map_view_content.grid(column='0', row='1', sticky='ew')
        self.frm_map_view_content.rowconfigure('1', weight='1')
        self.frm_map_view_content.columnconfigure('0', weight='1')
        self.frm_map_view.configure(height='200')
        self.frm_map_view.pack(side='top')
        self.content_window_top.add(self.frm_map_view, weight='1')
        self.graph_notebook = ttk.Notebook(self.content_window_top)
        self.graph_notebook.configure(height='200', width='200')
        self.graph_notebook.pack(side='top')
        self.content_window_top.add(self.graph_notebook, weight='1')
        self.content_window_top.configure(height='300', width='900')
        self.content_window_top.pack(side='top')
        self.content_container_window.add(self.content_window_top, weight='1')
        self.content_window_bottom = ttk.Panedwindow(
            self.content_container_window, orient='horizontal')
        self.frm_vessel = ttk.Frame(self.content_window_bottom)
        self.frm_vessel_menu = ttk.Frame(self.frm_vessel)
        self.frm_vessel_menu.configure(height='30', width='200')
        self.frm_vessel_menu.grid(sticky='new')
        self.frm_vessel_menu.rowconfigure('0', weight='1')
        self.frm_vessel_menu.columnconfigure('0', weight='1')
        self.frm_vessel_content = ttk.Frame(self.frm_vessel)
        self.frm_vessel_content.configure(height='270', width='200')
        self.frm_vessel_content.grid(row='1', sticky='ew')
        self.frm_vessel_content.rowconfigure('0', weight='1')
        self.frm_vessel_content.rowconfigure('1', weight='1')
        self.frm_vessel_content.columnconfigure('0', weight='1')
        self.frm_vessel.configure(height='200', width='200')
        self.frm_vessel.pack(side='top')
        self.content_window_bottom.add(self.frm_vessel, weight='1')
        self.frm_manouver = ttk.Frame(self.content_window_bottom)
        self.frm_manouver_menu = ttk.Frame(self.frm_manouver)
        self.frm_manouver_menu.configure(height='30', width='200')
        self.frm_manouver_menu.grid(sticky='new')
        self.frm_manouver_menu.rowconfigure('0', weight='1')
        self.frm_manouver_menu.columnconfigure('0', weight='1')
        self.frm_manouver_content = ttk.Frame(self.frm_manouver)
        self.frm_manouver_content.configure(height='200', width='200')
        self.frm_manouver_content.grid(row='1', sticky='ew')
        self.frm_manouver_content.rowconfigure('0', weight='1')
        self.frm_manouver_content.rowconfigure('1', weight='1')
        self.frm_manouver_content.columnconfigure('0', weight='1')
        self.frm_manouver.configure(height='270', width='200')
        self.frm_manouver.pack(side='top')
        self.content_window_bottom.add(self.frm_manouver, weight='1')
        self.content_window_bottom.configure(height='300', width='900')
        self.content_window_bottom.pack(side='top')
        self.content_container_window.add(self.content_window_bottom,
                                          weight='1')
        self.content_container_window.configure(height='200', width='900')
        self.content_container_window.pack(side='top')
        self.main_window.add(self.content_container_window, weight='1')
        self.main_window.configure(height='570', width='1024')
        self.main_window.grid(padx='10', pady='10', row='1', sticky='nsew')
        self.main_window.rowconfigure('0', weight='1')
        self.main_window.rowconfigure('1', uniform='None', weight='1000')
        self.main_window.columnconfigure('0', minsize='0', uniform='None',
                                         weight='1')
        self.frm_main_window.configure(height='600', width='1024')
        self.frm_main_window.grid(sticky='nsew')
        self.frm_main_window.rowconfigure('0', weight='1')
        self.frm_main_window.columnconfigure('0', weight='1')

        # Main widget
        self.mainwindow = self.frm_main_window

    def run(self):
        self.mainwindow.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindowApp(root)
    app.run()
