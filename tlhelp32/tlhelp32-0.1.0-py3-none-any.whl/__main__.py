"""TlHelp32 GUI - A demonstration of the `tlhelp32` package."""

from __future__ import annotations

import abc
import collections
import ctypes as c
import dataclasses as dt
import os
import pathlib
import queue
import threading
import tkinter as tk
from ctypes import wintypes as wt
from tkinter import messagebox, ttk
from typing import Deque

from ._base import BaseIterator
from .errors import CreationFailedError
from .heap import Heap, HeapBlock, HeapIterator
from .snapshot import Snapshot

ROOT: tk.Tk


class ShellPropertiesPage:
    class SHELLEXECUTEINFOW(c.Structure):
        class DUMMYUNION(c.Union):
            _fields_ = [("hIcon", wt.HICON), ("hMonitor", wt.HMONITOR)]

        _fields_ = [
            ("cbSize", wt.DWORD),
            ("fMask", wt.ULONG),
            ("hwnd", wt.HWND),
            ("lpVerb", wt.LPCWSTR),
            ("lpFile", wt.LPCWSTR),
            ("lpParameters", wt.LPCWSTR),
            ("lpDirectory", wt.LPCWSTR),
            ("nShow", c.c_int),
            ("hInstApp", wt.HINSTANCE),
            ("lpIDList", c.c_void_p),
            ("lpClass", wt.LPCWSTR),
            ("hkeyClass", wt.HKEY),
            ("dwHotKey", wt.DWORD),
            ("DUMMYUNIONNAME", DUMMYUNION),
            ("hProcess", wt.HANDLE),
        ]

    ShellExecuteExW = c.windll.shell32.ShellExecuteExW
    ShellExecuteExW.restype = wt.BOOL
    ShellExecuteExW.argtypes = [c.POINTER(SHELLEXECUTEINFOW)]

    SEE_MASK_INVOKEIDLIST = 12
    SW_SHOW = 5

    def __init__(self, path: str) -> None:
        self.info = self.SHELLEXECUTEINFOW()
        self.info.cbSize = c.sizeof(self.SHELLEXECUTEINFOW)
        self.info.fMask = self.SEE_MASK_INVOKEIDLIST
        self.info.hwnd = int(ROOT.frame(), 16)
        self.info.lpVerb = "properties"
        self.info.lpFile = path
        self.info.nShow = self.SW_SHOW

    def __call__(self) -> None:
        self.ShellExecuteExW(c.byref(self.info))


class HidingScrollbar(ttk.Scrollbar):
    def set(self, first: float, last: float) -> None:
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        super().set(first, last)


class SnapshotCreator(threading.Thread):
    def __init__(self, result_q: queue.Queue, exc_q: queue.Queue, pid: int):
        super().__init__()
        self._result = result_q
        self._exc = exc_q
        self._pid = pid

    def run(self) -> None:
        try:
            snap = Snapshot(self._pid)
        except CreationFailedError as exc:
            self._exc.put(exc)
        else:
            self._result.put(snap)


@dt.dataclass
class ColumnItem:
    attr: str
    name: str
    width: int = 80
    minwidth: int = 60


class BaseTVFrame(ttk.Frame, abc.ABC):
    _tab_name_ = ""
    _tab_idx_ = 0

    def __init__(self, master: ttk.Notebook, status: tk.StringVar):
        super().__init__(master)
        self._master = master
        self._count = 0
        self._status = status
        self.tv = ttk.Treeview(self)
        self.vsb = HidingScrollbar(self, orient="vertical", command=self.tv.yview)
        self.hsb = HidingScrollbar(self, orient="horizontal", command=self.tv.xview)
        self.tv.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tv.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.bind(
            "<<AddedToTab>>",
            lambda *_: self._master.tab(
                self._tab_idx_, text=f"{self._tab_name_} [{self._count}]"
            ),
        )

    def clear(self):
        self._count = 0
        for item in self.tv.get_children():
            self.tv.delete(item)

    def populate(self, iterator: BaseIterator) -> None:
        self.clear()


class BaseTableFrame(BaseTVFrame, abc.ABC):
    _columns_: list[ColumnItem] = []

    def __init__(self, master: ttk.Notebook, status: tk.StringVar):
        super().__init__(master, status)
        self.rm = tk.Menu(self.tv)
        self.tv.bind("<Button-3>", self.on_right_click)
        self.tv.configure(show="headings", columns=[col.attr for col in self._columns_])
        self._is_checked: list[tk.BooleanVar] = []
        for col in self._columns_:
            is_checked = tk.BooleanVar(value=True)
            self.tv.heading(col.attr, text=col.name)
            self.tv.column(
                col.attr, stretch=False, width=col.width, minwidth=col.minwidth
            )
            self.rm.add_checkbutton(
                label=col.name,
                command=self.menu_handler,
                variable=is_checked,
            )
            self._is_checked.append(is_checked)

    def menu_handler(self):
        displaycolumns = []
        for i in range(len(self._columns_)):
            if self._is_checked[i].get():
                displaycolumns.append(i)
        if displaycolumns:
            self.tv.configure(displaycolumns=displaycolumns)

    def on_right_click(self, event: tk.Event):
        if self.tv.identify_region(event.x, event.y) == "heading":
            self.rm.post(event.x_root, event.y_root)

    def populate(self, iterator: BaseIterator):
        super().populate(iterator)
        for obj in iterator:
            values = [getattr(obj, col.attr) for col in self._columns_]
            self.tv.insert("", "end", values=values)
            self._count += 1


class ModulesFrame(BaseTableFrame):
    _tab_name_ = "Modules"
    _tab_idx_ = 1
    _columns_ = [
        ColumnItem("base_addr", "Base address"),
        ColumnItem("name", "Name", 100),
        ColumnItem("size", "Size", 50),
        ColumnItem("handle", "Handle", 100),
        ColumnItem("path", "File path", 230),
    ]

    def __init__(self, master: ttk.Notebook, status: tk.StringVar):
        super().__init__(master, status)
        self.tv.bind("<Double-1>", self.on_dclick)
        self.tv.bind("<Motion>", lambda e: self.after(100, self.on_motion(e)))

    def on_dclick(self, event: tk.Event):
        column = self.tv.identify_column(event.x)
        try:
            heading = self.tv.heading(column, "text")
        except tk.TclError:
            return
        iid = self.tv.selection()[0]
        values = self.tv.item(iid, "values")
        path = values[4]
        if heading == "Name":
            ShellPropertiesPage(path)()
        if heading == "File path":
            pardir = pathlib.Path(path).parent
            os.startfile(pardir)  # nosec

    def on_motion(self, event: tk.Event):
        column = self.tv.identify_column(event.x)
        try:
            heading = self.tv.heading(column, "text")
        except tk.TclError:
            return
        if heading == "Name":
            self._status.set("Double-click to open Properties")
        elif heading == "File path":
            self._status.set("Double-click to open module directory")
        else:
            self._status.set("")


class ProcessesFrame(BaseTableFrame):
    _tab_name_ = "Processes"
    _tab_idx_ = 2
    _columns_ = [
        ColumnItem("pid", "Process ID"),
        ColumnItem("num_threads", "Thread count"),
        ColumnItem("parent", "Parent PID"),
        ColumnItem("priority", "Priority"),
        ColumnItem("name", "Name", 150),
    ]


class ThreadsFrame(BaseTableFrame):
    _tab_name_ = "Threads"
    _tab_idx_ = 3
    _columns_ = [
        ColumnItem("id_", "ID"),
        ColumnItem("owner", "Owner PID"),
        ColumnItem("priority", "Priority"),
    ]


class HeapsFrame(BaseTVFrame):
    _tab_name_ = "Heaps"
    _tab_idx_ = 0
    heap_fields = dt.fields(Heap)
    block_fields = dt.fields(HeapBlock)

    def __init__(self, master: ttk.Notebook, status: tk.StringVar):
        super().__init__(master, status)
        self._after_dq: Deque[str] = collections.deque(maxlen=1)
        self._is_child = False
        self.tv.configure(columns=("#1", "#2", "#3"))
        self.tv.column("#0", width=20, stretch=False)
        self.tv.heading("#1", text="Process ID")
        self.tv.heading("#2", text="Heap ID")
        self.tv.bind("<Leave>", lambda *_: self.on_leave())
        self.tv.bind("<Motion>", self.on_motion)
        self._top_levels: list[str] = []
        self._block_counts: list[int] = []

    def update(self, iid):
        # Tricks used to reduce CPU overload:
        # 1. after() removes sudden spikes in CPU usage.
        # 2. self._is_child checks if headings really need to be updated.
        # 3. Queue ensures the event queue isn't filled with junk
        def after_func():
            if self.tv.parent(iid):
                if not self._is_child:
                    self.tv.heading("#1", text="Base address")
                    self.tv.heading("#2", text="Type")
                    self.tv.heading("#3", text="Size")
                self._status.set("")
            else:
                if self._is_child:
                    self.tv.heading("#1", text="Process ID")
                    self.tv.heading("#2", text="Heap ID")
                    self.tv.heading("#3", text="")
                idx = self.tv.index(iid)
                count = self._block_counts[idx]
                self._status.set(f"{count} blocks in this heap")
            self._is_child = not self._is_child

        try:
            prev_id = self._after_dq.popleft()
        except IndexError:
            self._after_dq.append(self.after(10, after_func))
        else:
            self.after_cancel(prev_id)

    def on_motion(self, event: tk.Event):
        row = self.tv.identify_row(event.y)
        if row:
            self.update(row)
        else:
            self._status.set("")

    def on_leave(self):
        selection = self.tv.selection()
        if selection:
            self.update(selection[0])
        else:
            self._status.set("")

    def populate(self, iterator: HeapIterator):
        super().populate(iterator)
        for heap in iterator:
            values = [getattr(heap, attr.name) for attr in self.heap_fields]
            iid = self.tv.insert("", "end", values=values)
            self._top_levels.append(iid)
            self._block_counts.append(0)
            for block in heap:
                values = (block.start_addr, block.kind.name, block.size)
                self.tv.insert(iid, "end", values=values)
                self._block_counts[-1] += 1
            self._count += 1


class SearchFrame(ttk.Frame):
    def __init__(self, master: App, pidvar: tk.IntVar):
        super().__init__(master)
        self.lbl = ttk.Label(self, text="Process PID:")
        self.edit = ttk.Entry(self, textvariable=pidvar, font=("TxFixedFont", 10))
        self.btn = ttk.Button(
            self,
            command=lambda: master.event_generate("<<CreateSnapshot>>"),
            text="Create snapshot",
        )
        self.grid_columnconfigure(1, weight=1)
        self.lbl.grid(row=0, column=0, padx=5)
        self.edit.grid(row=0, column=1, padx=5, pady=1, sticky="nsew")
        self.btn.grid(row=0, column=2, padx=5, ipadx=3, ipady=3)


class App(tk.Tk):
    def __init__(self, pid: int = 0):
        global ROOT
        super().__init__()
        ROOT = self
        self.title("TlHelp32")
        self.geometry("600x400")
        self.option_add("*tearOff", False)
        style = ttk.Style()
        style.configure("Treeview", rowheight=24)
        # Remove borders from Treeview
        # https://riptutorial.com/tkinter/example/31885/customize-a-treeview
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nsew"})])

        self._pid = tk.IntVar(value=pid)
        self._status = tk.StringVar()
        self._result_q: queue.Queue[Snapshot] = queue.Queue(1)
        self._exc_q: queue.Queue[CreationFailedError] = queue.Queue(1)

        search = SearchFrame(self, self._pid)
        search.pack(fill="x", side="top", pady=(5, 0))
        nb = ttk.Notebook(self)
        self.heaps = HeapsFrame(nb, self._status)
        self.heaps.pack()
        self.modules = ModulesFrame(nb, self._status)
        self.modules.pack()
        self.processes = ProcessesFrame(nb, self._status)
        self.processes.pack()
        self.threads = ThreadsFrame(nb, self._status)
        self.threads.pack()
        nb.add(self.heaps, text="Heaps")
        nb.add(self.modules, text="Modules")
        nb.add(self.processes, text="Processes")
        nb.add(self.threads, text="Threads")
        nb.pack(fill="both", expand=True, pady=5, padx=5)
        sb = ttk.Label(self, textvariable=self._status)
        sb.pack(side="bottom", fill="x")
        self.bind("<<CreateSnapshot>>", lambda *_: self.populate())
        self.populate()

    def process_queue(self):
        try:
            exc = self._exc_q.get_nowait()
        except queue.Empty:
            pass
        else:
            messagebox.showerror("Snapshot creation failed", repr(exc))
            try:
                self.after_cancel(self._cancel_token)
            except ValueError:
                pass
            return
        try:
            self._snapshot = self._result_q.get_nowait()
        except queue.Empty:
            self._cancel_token = self.after(100, self.process_queue)
        else:
            self.heaps.populate(self._snapshot.heaps)
            self.modules.populate(self._snapshot.modules)
            self.processes.populate(self._snapshot.processes)
            self.threads.populate(self._snapshot.threads)
            for tab in (self.heaps, self.modules, self.processes, self.threads):
                tab.event_generate("<<AddedToTab>>")
            self.configure(cursor="arrow")

    def populate(self):
        self.configure(cursor="watch")
        SnapshotCreator(self._result_q, self._exc_q, self._pid.get()).start()
        self.process_queue()

    def destroy(self) -> None:
        try:
            if not self._snapshot.close():
                messagebox.showerror("Internal error", "Couldn't close snapshot handle")
        except AttributeError:
            pass
        return super().destroy()


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
