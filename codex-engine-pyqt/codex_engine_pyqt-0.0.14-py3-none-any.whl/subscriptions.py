from qtstrap import *
from codex import SerialDevice
from .bundles import SigBundle, SlotBundle


class SubscriptionManager(QObject):
    signals = {
        'add_device':[SerialDevice],
        'remove_device': [str]
    }
    slots = {
        'device_added': [SerialDevice], 
        'device_removed': [str],
        'subscribed': [None],
    }
    new_subscribers = []

    @classmethod
    def subscribe(cls, target):
        old_init = target.__init__

        def get_added():
            def on_device_added(self, device):
                self.devices[device.guid] = device
                if hasattr(self, 'device_added'):
                    self.device_added(device)
            return on_device_added

        def get_removed():
            def on_device_removed(self, guid):
                if hasattr(self, 'device_removed'):
                    self.device_removed(guid)
                self.devices.pop(guid)
            return on_device_removed

        def new_init(obj, *args, **kwargs):
            old_init(obj, *args, **kwargs)
            
            obj.signals = SigBundle(cls.signals)
            obj.slots = SlotBundle(cls.slots)
            obj.slots.link_to(obj)
            
            obj.devices = {}
            
            cls.new_subscribers.append(obj)

        target.on_device_added = get_added()
        target.on_device_removed = get_removed()

        target.__init__ = new_init

        return target

    @classmethod
    def subscribe_to(cls, device_name):

        def get_added():
            def on_device_added(self, device):
                if device.profile_name == device_name:
                    if self.device:
                        return
                    self.device = device
                    self.setEnabled(True)
                    if hasattr(self, 'connected'):
                        self.connected(device)
            return on_device_added

        def get_removed():
            def on_device_removed(self, guid):
                if self.device is None or self.device.guid != guid:
                    return
                self.device = None
                self.setEnabled(False)
                if hasattr(self, 'disconnected'):
                    self.disconnected(guid)
            return on_device_removed

        def decorator(target):
            target.on_device_added = get_added()
            target.on_device_removed = get_removed()

            old_init = target.__init__

            def new_init(obj, *args, **kwargs):
                old_init(obj, *args, **kwargs)
                
                obj.slots = SlotBundle(cls.slots)
                obj.slots.link_to(obj)

                obj.device = None
                obj.setEnabled(False)
                
                cls.new_subscribers.append(obj)

            target.__init__ = new_init

            return target
        return decorator
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.subscribers = []
        
        self.check_for_new_subscribers()

    def check_for_new_subscribers(self):
        for new_sub in self.new_subscribers:
            if new_sub not in self.subscribers:
                self.connect_subscriber(new_sub)
                
            self.new_subscribers.remove(new_sub)

    def connect_subscriber(self, subscriber):
        if hasattr(subscriber, 'slots'):
            if hasattr(subscriber.slots, 'device_added') and hasattr(subscriber.slots, 'device_removed'):
                self.parent().signals.device_added.connect(subscriber.slots.device_added)
                self.parent().signals.device_removed.connect(subscriber.slots.device_removed)
                
                for device in self.parent().devices:
                    subscriber.slots.device_added(self.parent().devices[device])
        
            if hasattr(subscriber.slots, 'subscribed'):
                subscriber.slots.subscribed()

        if hasattr(subscriber, 'signals'):
            if hasattr(subscriber.signals, 'add_device') and hasattr(subscriber.signals, 'remove_device'):
                subscriber.signals.add_device.connect(self.parent().slots.add_device)
                subscriber.signals.remove_device.connect(self.parent().slots.remove_device)