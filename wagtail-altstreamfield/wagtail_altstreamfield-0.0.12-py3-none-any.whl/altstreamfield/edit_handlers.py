from wagtail.admin.edit_handlers import FieldPanel

class AltStreamFieldPanel(FieldPanel):

    def classes(self):
        classes = super().classes()

        # remove the required class because the fields underneath this AltStreamField will do their own validation.
        if('required' in classes):
            classes.remove('required')

        classes.append('alt-stream-field')

        return classes