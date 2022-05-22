import select
import socket
import tkinter as tk
from collections import defaultdict
from functools import partial
from hashlib import md5
from threading import Thread
from tkinter.ttk import Scale, Separator, Scrollbar, Frame
from typing import Tuple, Callable, Optional, List

from ..common.auth import AuthenticationHeader
from ..common.constants import VOCAL_GROUPS
from ..common.log import logger
from ..common.message_board import MessageBoard
from ..common.message_protocol import MessageProtocol
from ..common.pace_maker import PaceMaker
from ..common.utils import to_db, to_gain, remove_non_ascii


class DeskChannel:
    def __init__(self, top, *,
                 name: str,
                 gid: int,
                 address: Tuple,
                 key: Optional[str] = None,
                 gain: float,
                 set_gain: Callable[[Tuple, str, float], None]):
        self.name = name
        self.gid = gid
        self.key = key
        self.address = address
        self.active = True
        self._set_gain = set_gain

        self._name_label = tk.Label(top, text=name)
        self._scale = Scale(top, from_=0, to=35, length=200, command=partial(set_gain, address, key))
        self._scale.set((to_db(gain) + 25 if gain else 0))

    def grid_forget(self):
        self._name_label.grid_forget()
        self._scale.grid_forget()

    def grid_add(self, row: int):
        self._name_label.grid(row=row, column=1, sticky='W')
        self._scale.grid(row=row, column=2, sticky='W')

    def change_address(self, new_address: Tuple):
        self.address = new_address
        self._scale.config(command=partial(self._set_gain, new_address, self.key))
        self._set_gain(new_address, self.key, self._scale.get())

    def update_active(self):
        self._scale.config(state=tk.NORMAL if self.active else tk.DISABLED)


class MixingDesk:
    def __init__(self, parent, config, destroy, set_monitor_level):
        self.root = tk.Toplevel(parent)
        self.root.title("Mixing Desk")
        self.root.protocol("WM_DELETE_WINDOW", destroy)
        canvas = tk.Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"),
                height=scrollable_frame.winfo_height(),
                width=scrollable_frame.winfo_width()
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.top = scrollable_frame
        self.changes = MessageBoard()
        self.config = config

        tk.Label(self.top, text="Status:").grid(row=0, column=0, sticky='W')
        self.status = tk.Label(self.top, text="Connecting...")
        self.status.grid(row=0, column=1, sticky='W')

        Separator(self.top).grid(row=1, column=0, columnspan=3, sticky='EW', pady=10)

        tk.Label(self.top, text='Monitor').grid(row=2, column=0, sticky='W')
        tk.Label(self.top, text='(not recorded)').grid(row=2, column=1, sticky='W')
        level_scale = Scale(self.top, from_=0, to=35, length=200,
                            command=set_monitor_level)
        initial_monitor_level = float(config.get('monitor_level', '-10'))
        level_scale.set(initial_monitor_level + 35)
        level_scale.grid(row=2, column=2, sticky='EW', padx=10)

        addr = config['server'], int(config['port']) - 20  # TODO: improve
        Thread(target=self._communicate, args=addr, name='mixing desk communicator').start()

        self._channel_list: List[DeskChannel] = []
        self._separators = []

    @staticmethod
    def singer_key(name, group) -> Optional[str]:
        if not name or group not in VOCAL_GROUPS[1:]:
            return None
        return md5((name + group).encode()).hexdigest()

    def _update_desk(self, sources):
        # deactivate all
        for channel in self._channel_list:
            channel.active = False

        # match channels with same address
        by_address = {channel.address: channel for channel in self._channel_list}
        to_match = []
        for source in sources:
            address = tuple(source['id'])
            try:
                channel = by_address[address]
            except KeyError:
                to_match.append(source)
                continue
            logger.debug(f"Matched channel with {address}")
            channel.active = True

        # match channels with same key
        by_key = defaultdict(list)
        for channel in self._channel_list:
            if not channel.active and channel.key is not None:
                by_key[channel.key].append(channel)
        to_add = []
        for source in to_match:
            key = self.singer_key(source['name'], source['group'])
            if key in by_key and by_key[key]:
                logger.debug(f"Matched channel with key {key}")
                channel = by_key[key].pop()
                address = tuple(source['id'])
                channel.change_address(address)
                channel.active = True
            else:
                source['key'] = key
                to_add.append(source)

        # add_missing channels
        if to_add:
            self._delete_channels()
            for source in to_add:
                clean_name = remove_non_ascii(source['name'])
                try:
                    gid = VOCAL_GROUPS.index(source['group'])
                except ValueError:
                    gid = 0
                if source['key'] and source['key'] in self.config:  # recover saved gain
                    gain = float(self.config[source['key']])
                    logger.debug(f"found saved gain for {clean_name} ({source['key']}) in config (gain={gain})")
                else:
                    gain = source['gain']
                logger.debug(f"Adding channel for {clean_name} gid {gid} key {source['key']}")
                self._channel_list.append(DeskChannel(self.top, name=source['name'], gid=gid, key=source['key'],
                                                      address=tuple(source['id']), gain=gain, set_gain=self._set_gain))
            self._channel_list.sort(key=lambda ch: (ch.gid, ch.name))
            self._add_channels()

        # update activity
        for channel in self._channel_list:
            channel.update_active()

    def _delete_channels(self):
        for channel in self._channel_list:
            channel.grid_forget()
        for separator in self._separators:
            separator.grid_forget()
        self._separators = []

    def _add_channels(self):
        assert not self._separators
        row = 3
        gid = -1
        for channel in self._channel_list:
            if channel.gid != gid:
                gid = channel.gid
                self._separators.append(Separator(self.top))
                self._separators[-1].grid(row=row, column=0, columnspan=3, sticky='EW', pady=10)
                row += 1
                self._separators.append(tk.Label(self.top, text=VOCAL_GROUPS[gid]))
                self._separators[-1].grid(row=row, column=0, sticky='W')
            channel.grid_add(row)
            row += 1

    def _refresh_sources(self, conn):
        conn.send(MessageProtocol({"action": "list"}).to_bytes())
        logger.debug("Command sent")
        res, _, err = select.select((conn,), (), (conn,), 1.0)
        if not res:
            logger.error("failed to get list")
            raise RuntimeError("failed to get list")
        data = conn.recv(2)
        msg = MessageProtocol.from_bytes(conn.recv(MessageProtocol.get_length(data)))
        logger.debug(f"Received list with {len(msg.msg)} sources")

        self._update_desk(msg.msg)

    def _communicate(self, host, port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug(f"Connecting to {host}:{port}...")
        conn.connect((host, port))
        logger.debug("Connected")
        conn.send(AuthenticationHeader().to_bytes())
        self.status.config(text="Connected")
        try:
            self._refresh_sources(conn)
        except RuntimeError:
            self.status.config(text="Disconnected")
            conn.close()
            return

        # process messages
        timer = PaceMaker(0.1, len(self._channel_list))
        for source_id, gain in self.changes.messages():
            if source_id == 'update':
                try:
                    self._refresh_sources(conn)
                except RuntimeError:
                    self.status.config(text="Disconnected")
                    break
            else:
                timer.pace()
                msg = MessageProtocol({'action': 'adjust_gain', 'id': source_id, 'gain': gain})
                _, ready, err = select.select((), (conn,), (conn,), 1.0)
                if not ready:
                    logger.error("socket not ready")
                    self.status.config(text="Disconnected")
                    break
                logger.debug(f"send {msg.msg}")
                conn.send(msg.to_bytes())
        conn.close()
        logger.info("communication thread ended")

    def _set_gain(self, source_id: Tuple, key: Optional[str], fader_value):
        fader_value = float(fader_value)
        gain = to_gain(fader_value - 25) if fader_value > 0 else 0
        if key:
            self.config[key] = str(gain)
        self.changes.post_message(source_id, gain)

    def destroy(self):
        self.changes.close()
        self.root.destroy()

    def trigger_update(self):
        self.changes.post_message('update', True)
