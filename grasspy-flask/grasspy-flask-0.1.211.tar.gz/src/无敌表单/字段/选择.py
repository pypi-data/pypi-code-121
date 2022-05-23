import itertools

from wtforms import widgets
from .核心 import 〇字段
from wtforms.validators import ValidationError

__all__ = (
    "〇选择框字段",
    "〇多选字段",
    "〇单选字段",
)


class SelectFieldBase(〇字段):
    option_widget = widgets.Option()

    """
    Base class for fields which can be iterated to produce options.

    This isn't a field, but an abstract base class for fields which want to
    provide this functionality.
    """

    def __init__(self, 标签=None, 验证器々=None, option_widget=None, **kwargs):
        super().__init__(标签, 验证器々, **kwargs)

        if option_widget is not None:
            self.option_widget = option_widget

    def iter_choices(self):
        """
        Provides data for choice widget rendering. Must return a sequence or
        iterable of (value, label, selected) tuples.
        """
        raise NotImplementedError()

    def has_groups(self):
        return False

    def iter_groups(self):
        raise NotImplementedError()

    def __iter__(self):
        opts = dict(
            部件=self.option_widget,
            验证器々=self.validators,
            name=self.name,
            render_kw=self.render_kw,
            _form=None,
            _meta=self.meta,
        )
        for i, (value, 标签, checked) in enumerate(self.iter_choices()):
            opt = self._Option(标签=标签, id="%s-%d" % (self.id, i), **opts)
            opt.process(None, value)
            opt.checked = checked
            yield opt

    class _Option(〇字段):
        checked = False

        def _value(self):
            return str(self.data)


class 〇选择框字段(SelectFieldBase):
    widget = widgets.Select()

    def __init__(
        self,
        标签=None,
        验证器々=None,
        coerce=str,
        选择々=None,
        validate_choice=True,
        **kwargs,
    ):
        super().__init__(标签, 验证器々, **kwargs)
        self.coerce = coerce
        if callable(选择々):
            选择々 = 选择々()
        if 选择々 is not None:
            self.选择々 = 选择々 if isinstance(选择々, dict) else list(选择々)
        else:
            self.选择々 = None
        self.validate_choice = validate_choice

    def iter_choices(self):
        if not self.选择々:
            选择々 = []
        elif isinstance(self.选择々, dict):
            选择々 = list(itertools.chain.from_iterable(self.选择々.values()))
        else:
            选择々 = self.选择々

        return self._choices_generator(选择々)

    def has_groups(self):
        return isinstance(self.选择々, dict)

    def iter_groups(self):
        if isinstance(self.选择々, dict):
            for 标签, 选择々 in self.选择々.items():
                yield (标签, self._choices_generator(选择々))

    def _choices_generator(self, 选择々):
        if not 选择々:
            _choices = []

        elif isinstance(选择々[0], (list, tuple)):
            _choices = 选择々

        else:
            _choices = zip(选择々, 选择々)

        for value, 标签 in _choices:
            yield (value, 标签, self.coerce(value) == self.data)

    def process_data(self, value):
        try:
            # If value is None, don't coerce to a value
            self.data = self.coerce(value) if value is not None else None
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        try:
            self.data = self.coerce(valuelist[0])
        except ValueError as exc:
            raise ValueError(self.gettext("Invalid Choice: could not coerce.")) from exc

    def pre_validate(self, form):
        if self.选择々 is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        if not self.validate_choice:
            return

        for _, _, match in self.iter_choices():
            if match:
                break
        else:
            raise ValidationError(self.gettext("Not a valid choice."))


class 〇多选字段(〇选择框字段):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices.  You'll need to specify the HTML `size`
    attribute to the select field when rendering.
    """

    widget = widgets.Select(multiple=True)

    def _choices_generator(self, 选择々):
        if 选择々:
            if isinstance(选择々[0], (list, tuple)):
                _choices = 选择々
            else:
                _choices = zip(选择々, 选择々)
        else:
            _choices = []

        for value, 标签 in _choices:
            selected = self.data is not None and self.coerce(value) in self.data
            yield (value, 标签, selected)

    def process_data(self, value):
        try:
            self.data = list(self.coerce(v) for v in value)
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        try:
            self.data = list(self.coerce(x) for x in valuelist)
        except ValueError as exc:
            raise ValueError(
                self.gettext(
                    "Invalid choice(s): one or more data inputs could not be coerced."
                )
            ) from exc

    def pre_validate(self, form):
        if self.选择々 is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        if not self.validate_choice or not self.data:
            return

        acceptable = {c[0] for c in self.iter_choices()}
        if any(d not in acceptable for d in self.data):
            unacceptable = [str(d) for d in set(self.data) - acceptable]
            raise ValidationError(
                self.ngettext(
                    "'%(value)s' is not a valid choice for this field.",
                    "'%(value)s' are not valid choices for this field.",
                    len(unacceptable),
                )
                % dict(value="', '".join(unacceptable))
            )


class 〇单选字段(〇选择框字段):
    """
    Like a SelectField, except displays a list of radio buttons.

    Iterating the field will produce subfields (each containing a label as
    well) in order to allow custom rendering of the individual radio fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()
