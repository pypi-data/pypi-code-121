from plone.z3cform.interfaces import ISubformFactory
from z3c.form import form
from z3c.form import interfaces
from z3c.form.field import Fields

import zope.component
import zope.interface


@zope.interface.implementer(interfaces.ISubForm)
class ObjectSubForm(form.BaseForm):

    def __init__(self, context, request, parentWidget):
        self.context = context
        self.request = request
        self.__parent__ = parentWidget
        self.parentForm = parentWidget.form
        self.ignoreContext = self.__parent__.ignoreContext
        self.ignoreRequest = self.__parent__.ignoreRequest
        if interfaces.IFormAware.providedBy(self.__parent__):
            self.ignoreReadonly = self.parentForm.ignoreReadonly
        self.prefix = self.__parent__.name

    def _validate(self):
        for widget in self.widgets.values():
            try:
                # convert widget value to field value
                converter = interfaces.IDataConverter(widget)
                value = converter.toFieldValue(widget.value)
                # validate field value
                zope.component.getMultiAdapter(
                    (self.context,
                     self.request,
                     self.parentForm,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(value, force=True)
            except (zope.schema.ValidationError, ValueError) as error:
                # on exception, setup the widget error message
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.parentForm, self.context),
                    interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view

    def setupFields(self):
        self.fields = Fields(self.__parent__.field.schema)

    def update(self):
        if self.__parent__.field is None:
            raise ValueError("%r .field is None, that's a blocking point" % self.__parent__)
        #update stuff from parent to be sure
        self.mode = self.__parent__.mode

        self.setupFields()

        super(ObjectSubForm, self).update()

    def getContent(self):
        return self.__parent__._value


@zope.interface.implementer(ISubformFactory)
class SubformAdapter(object):
    """Most basic-default subform factory adapter"""
    zope.component.adapts(zope.interface.Interface, #widget value
                          interfaces.IFormLayer,    #request
                          zope.interface.Interface, #widget context
                          zope.interface.Interface, #form
                          interfaces.IObjectWidget, #widget
                          zope.interface.Interface, #field
                          zope.interface.Interface) #field.schema

    factory = ObjectSubForm

    def __init__(self, context, request, widgetContext, form,
                 widget, field, schema):
        self.context = context
        self.request = request
        self.widgetContext = widgetContext
        self.form = form
        self.widget = widget
        self.field = field
        self.schema = schema

    def __call__(self):
        obj = self.factory(self.context, self.request, self.widget)
        return obj
