from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("napari-spacemouse")
except PackageNotFoundError:
    __version__ = "unknown"

__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"


from napari_spacemouse import _spacemouse


def uninstall():
    _spacemouse.stop()


def install(device: str = None):
    """Make napari spacemouse-aware.

    This will cause movements of any 3DConnexion mouse to alter the state of the
    viewer camera.

    Parameters
    ----------
    device : str, optional
        Name of a device to use. By default the first compatible device found will
        be used.  Valid names include:
            'SpaceNavigator',
            'SpaceMouse Compact',
            'SpaceMouse Pro Wireless',
            'SpaceMouse Pro',
            'SpaceMouse Wireless',
            '3Dconnexion Universal Receiver',
            'SpacePilot Pro'
    """
    from napari_spacemouse import _napari

    if _spacemouse._active_device is not None:
        if device and _spacemouse._active_device.name != device:
            raise RuntimeError("Spacemouse already installed. Please uninstall first")
        _spacemouse.run()
        return

    if dev := _spacemouse.open(
        callback=_napari._apply_state_to_viewer,
        button_callback=_napari._handle_buttons,
        device=device,
    ):
        dev.run()


if __name__ == "__main__":
    import napari

    install()

    viewer = napari.Viewer(ndisplay=3)
    viewer.axes.visible = True
    viewer.open_sample("napari", "brain")
    napari.run()
