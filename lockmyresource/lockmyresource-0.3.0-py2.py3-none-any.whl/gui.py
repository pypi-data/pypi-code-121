#!/usr/bin/env python3

import datetime
import json
import logging
import os
import sqlite3
import sys
import tkinter as tk
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from tkinter import simpledialog
from tkinter import filedialog
from typing import Callable, List, Dict, Optional, Set

import metainfo
from configfile import LockMyResourceConfigFile
from core import User, no_user, Core, Database, Resource, LockRecord, github_url
from util import traced, memprofiled
from tableformatter import JsonFormatter


github_logo_filename = "github25.png"


class Subscriptions:
    def __init__(self):
        self.subscribed_to_names: Set[str] = set()

    def is_subscribed_to(self, lock_record: LockRecord) -> bool:
        return lock_record.resource.name in self.subscribed_to_names

    def subscribe(self, lock_record: LockRecord):
        self.subscribed_to_names.add(lock_record.resource.name)

    def unsubscribe(self, lock_record: LockRecord):
        if lock_record.resource.name in self.subscribed_to_names:
            self.subscribed_to_names.remove(lock_record.resource.name)


class LockRecordLockCommand:
    def __init__(self, lock_record: LockRecord, refresh_command: Callable[[str], None], get_lock_comment):
        self.lock_record = lock_record
        self.text = "Lock"
        self.refresh_command = refresh_command
        self.get_lock_comment = get_lock_comment


    def execute(self):
        success = self.lock_record.lock(self.get_lock_comment())
        resource = self.lock_record.resource.name
        message = f"Lock acquired on {resource}" if success else f"Couldn't lock {resource}"
        self.refresh_command(message)


class LockRecordReleaseCommand:
    def __init__(self, lock_record: LockRecord, refresh_command: Callable[[str], None]):
        self.lock_record = lock_record
        self.text = "Release"
        self.refresh_command = refresh_command
    
    def execute(self):
        success = self.lock_record.release()
        resource = self.lock_record.resource.name
        message = f"Lock released on {resource}" if success else f"Couldn't release {resource}"
        self.refresh_command(message)


class LockRecordSubscriptionCommand:
    def __init__(self, lock_record: LockRecord, refresh_command: Callable[[str], None], subscriptions: Subscriptions) -> None:
        self.lock_record = lock_record
        self.subscriptions = subscriptions
        self.text = "Unsubscribe" if subscriptions.is_subscribed_to(lock_record) else "Subscribe"
        self.refresh_command = refresh_command
    
    def execute(self):
        resource = self.lock_record.resource.name
        if self.subscriptions.is_subscribed_to(self.lock_record):
            self.subscriptions.unsubscribe(self.lock_record)
            message = f"Unsubscribed from {resource}"
        else:
            self.subscriptions.subscribe(self.lock_record)
            message = f"Subscribed to {resource}, you'll be notified when it gets free"
        self.refresh_command(message)


class LockWidget(tk.Frame):
    def __init__(self, master, core: Core, refresh_command, get_lock_comment, restore_window: Callable[[], None]):
        super().__init__(master)
        self.core = core
        self.refresh_command = refresh_command
        self.get_lock_comment = get_lock_comment
        self.restore_window = restore_window
        self.cells = {}
        self.rows_count = 0
        column_heads = ["Resource", "User", "Locked at", "Comment", "Command"]
        for x, column_head in enumerate(column_heads):
            head = tk.Label(self, text=column_head)
            head.grid(row=0, column=x, sticky="NEWS")
        self.subscriptions = Subscriptions()

    def update(self, locks: List[LockRecord]):
        for y in range(self.rows_count):
            for grid_cell in self.grid_slaves(row=1 + y):
                grid_cell.grid_forget()
                grid_cell.destroy()
                del grid_cell

        for y, row in enumerate(locks):
            y += 1
            self.set_cell(0, y, tk.Label(self, text=row.resource.name, relief=tk.RIDGE))
            self.set_cell(1, y, tk.Label(self, text=row.user.login, relief=tk.RIDGE))
            self.set_cell(2, y, tk.Label(self, text=row.locked_at, relief=tk.RIDGE))
            self.set_cell(3, y, tk.Label(self, text=row.comment, relief=tk.RIDGE))

            command = None
            if row.user == self.core.user:
                command = LockRecordReleaseCommand(row, self.refresh_command)
                self.subscriptions.unsubscribe(row)
            elif row.user == no_user:
                command = LockRecordLockCommand(row, self.refresh_command, self.get_lock_comment)
                self.check_subscriptions(row)
            else:
                command = LockRecordSubscriptionCommand(row, self.refresh_command, self.subscriptions)

            if command is not None:
                self.set_cell(4, y, tk.Button(self, text=command.text, command=command.execute))

        self.rows_count = len(locks)

    def check_subscriptions(self, lock_record: LockRecord):
        if not self.subscriptions.is_subscribed_to(lock_record):
            return

        self.subscriptions.unsubscribe(lock_record)
        self.refresh_command(f"{lock_record.resource.name} is available, lock it while you can!")
        self.restore_window()

    def set_cell(self, x: int, y: int, cell: tk.BaseWidget):
        cell.grid(row=y, column=x, sticky="NEWS")


class Application(tk.Frame):
    def __init__(self, master: tk.Tk, core: Core):
        super().__init__(master)
        self.core = core
        self.pack()

        self.locks_widget = LockWidget(self, self.core, self.refresh_command, self.get_lock_comment, self.restore_window)
        self.locks_widget.pack(side=tk.TOP)

        self.text_panel = tk.Frame(self)
        self.text_panel.pack()

        self.lock_comment_label = tk.Label(self.text_panel, text="Lock comment ")
        self.lock_comment_label.grid(row=0, column=0, sticky="W")

        self.lock_comment = tk.Text(self.text_panel, state=tk.NORMAL, height=1)
        def ignore_enter(event):
            if event.keysym == "Return":
                return "break"

        self.lock_comment.bind("<Key>", ignore_enter)
        self.lock_comment.grid(row=0, column=1, sticky="NEWS")

        self.status_label = tk.Label(self.text_panel, text="Status ")
        self.status_label.grid(row=1, column=0, sticky="W")

        self.status = tk.Text(self.text_panel, state=tk.DISABLED, height=1)
        self.status.grid(row=1, column=1, sticky="NEWS")

        self.buttons = tk.Frame()
        self.buttons.pack()

        self._github_logo = tk.PhotoImage(file=Path(__file__).parent / github_logo_filename)
        self.github = tk.Button(self.buttons, text="GitHub", image=self._github_logo, compound=tk.LEFT,
                                command=self.github_command)
        self.github.pack(side=tk.LEFT, fill=tk.Y)

        self.open_db = tk.Button(self.buttons, text="Open DB", command=self.open_db_command)
        self.open_db.pack(side=tk.LEFT, fill=tk.Y)

        self.quit = tk.Button(self.buttons, text="Quit", command=self.master.destroy)
        self.quit.pack(side=tk.LEFT, fill=tk.Y)

        self.refresh = tk.Button(self.buttons, text = "Refresh", command=self.refresh_command)
        self.refresh.pack(side=tk.LEFT, fill=tk.Y)

        self.refresh_command(self.core.database.info())

    def restore_window(self):
        self.master.deiconify()
        self.master.attributes('-topmost', 1)
        self.master.lift()
        self.master.focus()
        self.master.focus_force()
        self.master.attributes('-topmost', 0)

    #@memprofiled
    def refresh_command(self, message: Optional[str] = "List updated"):
        with self.attempt("Failed to load data"):
            self.locks_widget.update(self.core.list())
            if message is not None:
                self.show_message(message)

    def attempt(self, failure_message: str):
        def on_error():
            self.show_message(failure_message)

        class ContextManager:
            def __init__(self, on_error: callable):
                self.on_error = on_error

            def __enter__(self):
                return self

            def __exit__(self, type, value, traceback):
                if type is not None:
                    logging.exception(failure_message)
                    self.on_error()
                return True
        
        return ContextManager(on_error)

    def show_message(self, message):
        if isinstance(message, list):
            self.status.height = len(message)
            message = "\n".join(message)
        else:
            self.status.height = 1

        message = with_time(message)
        logging.info(message)
        self.status.configure(state=tk.NORMAL)
        self.status.delete("1.0", tk.END)
        self.status.insert(tk.END, message)
        self.status.configure(state=tk.DISABLED)

    def get_lock_comment(self):
        return self.lock_comment.get("1.0", tk.END).strip()

    def open_db_command(self):
        dbfilename = filedialog.askopenfilename(
            parent=self,
            title="Choose DB file",
            initialdir=self.core.database.get_dbdir(),
            initialfile=self.core.database.get_dbfile(),
            filetypes=[(".DB file", "*.db")]
            )
        if not dbfilename:
            return
        database = Database.open(Path(dbfilename))
        self.core.switch_database(database)
        self.refresh_command(self.core.database.info())
        if isinstance(database, Database):
            self.save_dbfile_config()

    def save_dbfile_config(self):
        configfile = LockMyResourceConfigFile()
        config = configfile.read_config()
        config.dbfile = str(self.core.database.dbfile)
        configfile.write_config(config)

    def github_command(self):
        self.show_message(f"Opening {github_url} in a browser")
        webbrowser.open(github_url)


class ApplicationRefresher:
    def __init__(self, app: Application, root: tk.Tk, refresh_interval_millis: int):
        self.app = app
        self.root = root
        self.refresh_interval_millis = refresh_interval_millis

    def refresh(self):
        self.app.refresh_command(message=None)
        self.root.after(self.refresh_interval_millis, self.refresh)


def with_time(text: str) -> str:
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return f"{now} {text}"


@traced
def init_user(root) -> User:
    user = User.from_os()
    if user != no_user:
        return user
    configfile = LockMyResourceConfigFile()
    config = configfile.read_config()
    if config.user is not None:
        return User(config.user)
    username = simpledialog.askstring("User", "Enter username:", parent=root)
    config.user = username
    configfile.write_config(config)
    return User(username)


@traced
def init_db(default_path: str) -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    configfile = LockMyResourceConfigFile()
    config = configfile.read_config()
    if config.dbfile is None:
        config.dbfile = default_path
        configfile.write_config(config)
    return Path(config.dbfile)


def main():
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    user = init_user(root)
    logging.info("User: %s", user)
    root.title(f"Lock My Resource {metainfo.version}")
    dbfile = init_db("lockmyresource.db")
    core = Core(user, Database.open(dbfile), JsonFormatter())
    app = Application(root, core)
    refresher = ApplicationRefresher(app, root, 5000)
    root.after(500, refresher.refresh)
    app.mainloop()


if __name__ == "__main__":
    main()
