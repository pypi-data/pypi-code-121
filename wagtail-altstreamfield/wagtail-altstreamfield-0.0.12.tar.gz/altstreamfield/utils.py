from django.forms.widgets import Media

def get_class_media(base, instance):
    '''Convenience function to be used when overriding the `media` property.

    This function maintains the tasks of the media property set up by
    `MediaDefiningClass` but allows you to extend the normal behavior.

    Use:
    class MyClass(Block):
        def media(self):
            media = get_classMedia(super().media(), self)
            # ... do extra stuff here ...
            return media
    '''
    definition = getattr(instance, 'Media', None)
    if definition:
        extend = getattr(definition, 'extend', True)
        if extend:
            if extend is True:
                m = base
            else:
                m = Media()
                for medium in extend:
                    m = m + base[medium]
            return m + Media(definition)
        return Media(definition)
    else:
        return base