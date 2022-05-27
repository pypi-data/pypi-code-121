from . import ViewportConfiguration

# Here only for backward compatibility with OVITO 2.9.0:
def _ViewportConfiguration__len__(self):
    return len(self.viewports)
ViewportConfiguration.__len__ = _ViewportConfiguration__len__

# Here only for backward compatibility with OVITO 2.9.0:
def _ViewportConfiguration__iter__(self):
    return self.viewports.__iter__()
ViewportConfiguration.__iter__ = _ViewportConfiguration__iter__

# Here only for backward compatibility with OVITO 2.9.0:
def _ViewportConfiguration__getitem__(self, index):
    return self.viewports[index]
ViewportConfiguration.__getitem__ = _ViewportConfiguration__getitem__
