#!/usr/bin/env python3
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify


class BgmacgyverIndicator:

    APPID = "bgmacgyver"
    USERNAME = os.getenv("BGMACGYVER_USERNAME", default=os.getenv("USER"))
    IRB_USER = os.getenv("BGMACGYVER_IRB_USER", default=USERNAME)

    BASE = os.path.abspath(os.path.dirname(__file__))
    SVG_ON = os.path.join(BASE, 'on.svg')
    SVG_OFF = os.path.join(BASE, 'off.svg')
    SVG_LOADING = os.path.join(BASE, 'loading.svg')

    CMD_OPEN = "/usr/bin/nautilus /workspace"
    CMD_TERMINAL = "x-terminal-emulator -x ssh -p 22022 {}@bbgcluster".format(IRB_USER)

    IRB_MOUNT_PROJECTS = "sshfs -p 22022 {}@bbgcluster:/workspace/projects /workspace/projects -o reconnect -o idmap=user -o nonempty".format(IRB_USER)
    IRB_MOUNT_DATASETS = "sshfs -p 22022 {}@bbgcluster:/workspace/datasets /workspace/datasets -o reconnect -o idmap=user -o nonempty".format(IRB_USER)
    IRB_MOUNT_USERS = "sshfs -p 22022 {}@bbgcluster:/home /workspace/users -o reconnect -o idmap=user -o nonempty".format(IRB_USER)
    IRB_MOUNT_NO_BACKUP = "sshfs -p 22022 {}@bbgcluster:/workspace/nobackup /workspace/nobackup -o reconnect -o idmap=user -o nonempty".format(IRB_USER)
    IRB_MOUNT_DATASAFE = "sshfs -p 22022 {}@bbgcluster:/workspace/datasafe /workspace/datasafe -o reconnect -o idmap=user -o nonempty".format(IRB_USER)
    IRB_UMOUNT_PROJECTS = "sudo umount -l /workspace/projects"
    IRB_UMOUNT_DATASETS = "sudo umount -l /workspace/datasets"
    IRB_UMOUNT_USERS = "sudo umount -l /workspace/users"
    IRB_UMOUNT_NO_BACKUP = "sudo umount -l /workspace/nobackup"
    IRB_UMOUNT_DATASAFE = "sudo umount -l /workspace/nobackup"

    def __init__(self):

        notify.init(self.APPID)
        self.ind = appindicator.Indicator.new(self.APPID, "", appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.ind.set_icon(self.SVG_OFF)
        self.ind.set_attention_icon(self.SVG_LOADING)
        self.ind.set_menu(self.build_menu())

        self.lock = False
        gtk.main()

    def build_menu(self):
        menu = gtk.Menu()

        # Connection
        item_connect = gtk.MenuItem('Connect')
        item_connect.connect("activate", self.action_connect)
        menu.append(item_connect)
        item_disconnect = gtk.MenuItem('Disconnect')
        item_disconnect.connect('activate', self.action_disconnect)
        menu.append(item_disconnect)
        menu.append(gtk.SeparatorMenuItem())

        # Open terminals & folders
        item_mount = gtk.MenuItem('Open /workspace')
        item_mount.connect('activate', self.open_workspace)
        menu.append(item_mount)
        item_term = gtk.MenuItem('Remote terminal')
        item_term.connect('activate', self.term)
        menu.append(item_term)
        menu.append(gtk.SeparatorMenuItem())

        # Exit
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def action_connect(self, source):
        self.connect()

    def action_disconnect(self, source):
        self.disconnect()

    def connect(self):

        if not self.lock:
            self.lock = True
            self.ind.set_status(appindicator.IndicatorStatus.ATTENTION)

            mounted = True
            ec = os.system(self.IRB_MOUNT_PROJECTS)
            mounted = mounted and ec == 0

            ec = os.system(self.IRB_MOUNT_DATASETS)
            mounted = mounted and ec == 0

            ec = os.system(self.IRB_MOUNT_USERS)
            mounted = mounted and ec == 0

            ec = os.system(self.IRB_MOUNT_NO_BACKUP)
            mounted = mounted and ec == 0

            ec = os.system(self.IRB_MOUNT_DATASAFE)
            mounted = mounted and ec == 0

            if mounted:
                self.ind.set_icon(self.SVG_ON)
                self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
            else:
                self.ind.set_icon(self.SVG_OFF)
                self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)

            self.lock = False

    def disconnect(self):

        if not self.lock:
            self.lock = True
            self.ind.set_status(appindicator.IndicatorStatus.ATTENTION)

            unmounted = True
            ec = os.system(self.IRB_UMOUNT_PROJECTS)
            unmounted = unmounted and ec == 0

            ec = os.system(self.IRB_UMOUNT_DATASETS)
            unmounted = unmounted and ec == 0

            ec = os.system(self.IRB_UMOUNT_USERS)
            unmounted = unmounted and ec == 0

            ec = os.system(self.IRB_UMOUNT_NO_BACKUP)
            unmounted = unmounted and ec == 0

            ec = os.system(self.IRB_UMOUNT_DATASAFE)
            unmounted = unmounted and ec == 0

            if unmounted:
                self.ind.set_icon(self.SVG_OFF)
                self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)

            self.lock = False

    def open_workspace(self, source):
        os.system(self.CMD_OPEN)

    def term(self, source):
        os.system(self.CMD_TERMINAL)

    def quit(self, source):
        self.disconnect()
        notify.uninit()
        gtk.main_quit()


def cmdline():
    instance = BgmacgyverIndicator()


if __name__ == "__main__":
    cmdline()
