"""
    Admin utils
"""
import logging

from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib.admin import FieldListFilter, RelatedFieldListFilter
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from django_autoutils.html_tag import get_edit_link, get_edit_icon, get_avatar_image, get_edit_url, get_pretty_json

logger = logging.getLogger("django_autoutils")


class AutoCompleteFieldListFilter(FieldListFilter):
    """
        Empty class
    """
    pass


def admin_display(function=None, *, label=None, description=None, ordering=None, allow_tags=None):
    """
        Set Data for change action
    """

    def decorator(func):
        """
            Decorator
        """
        if label is not None:
            func.label = label
        if description is not None:
            func.short_description = description
        if ordering is not None:
            func.admin_order_field = ordering
        if allow_tags is not None:
            func.allow_tags = allow_tags
        return func

    if function is None:
        return decorator
    else:
        return decorator(function)


class CountRelatedFieldListFilter(RelatedFieldListFilter):
    """
        Use this class for showing a beautiful dropdown in django list filter
        Add count of related in name and sort by count
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model: "models.Model" = model
        super().__init__(field, request, params, model, model_admin, field_path)

    def field_choices(self, field, request, model_admin):
        """
            Change this class for reach goal
        """
        ordering = self.field_admin_ordering(field, request, model_admin)
        choices = field.get_choices(include_blank=False, ordering=ordering)
        choices_dict = {}
        for choice in choices:
            pk, name = choice
            choices_dict[pk] = name
        pk_name = self.model._meta.pk.name
        count_field = pk_name + "__count"
        query_set: "models.query.QuerySet" = self.model.objects.values(self.field_path).annotate(models.Count(pk_name))
        query_set = query_set.order_by("-" + count_field)
        result = []
        for query in query_set:
            field_id = query.get(self.field_path)
            count = query.get(count_field)
            result.append(
                (field_id, f"{choices_dict.get(field_id)} ({count})")
            )
        return result


class CountRelatedDropdownFilter(CountRelatedFieldListFilter):
    """
        Use this class for showing a beautiful dropdown in django list filter
    """
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'


class EditLinkAdmin:
    """
        Use this class for adding an edit link for object(s)
    """
    edit_text = "edit"

    def _get_edit_text(self, obj):
        return self.edit_text

    @admin_display(description=_("edit"), allow_tags=True)
    def edit_link(self, obj):
        """
            Edit link in admin panel
        """
        try:
            return get_edit_link(obj, f"{self._get_edit_text(obj)}")
        except Exception as e:
            logger.error(f"edit link for {obj} has error {e}")
        return None


class LimitForeignKeyAdmin:
    """
        Use this class for common work in limit foreignkey queryset
    """
    obj = None

    def get_form(self, request, obj=None, **kwargs):
        """
            Set id of current object in object_id field
        """
        self.obj = obj
        # noinspection PyUnresolvedReferences
        return super().get_form(request, obj, **kwargs)

    def _get_foreignkey_queryset(self, request, db_field):
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
            Base function for django model admin class
        """
        queryset = self._get_foreignkey_queryset(request, db_field.name)
        if queryset is not None:
            kwargs["queryset"] = queryset
        # noinspection PyUnresolvedReferences
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class InlineRelatedAdmin:
    """
        Use this class for change inline objects before showing
    """

    def _handle_inline_obj(self, inline, obj):
        inline.instance = obj
        if hasattr(inline, "_handle_instance"):
            # noinspection PyProtectedMember
            inline._handle_instance(obj)

    def _check_inline_obj(self, request, inline, obj):
        return True

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Yield formsets and the corresponding inlines.
        """
        if not obj:
            return
        # noinspection PyUnresolvedReferences
        for inline in self.get_inline_instances(request, obj):
            inline.request = request
            self._handle_inline_obj(inline, obj)
            if self._check_inline_obj(request, inline, obj):
                yield inline.get_formset(request, obj), inline


def avatar_wrapper(func):
    """
        Same function for this job
        Args:
            func : input function
    """

    def wrapper(self, obj):
        """
            Same function for this job
        Args:
            self (AvatarAdmin):
            obj: object
        """
        if not obj:
            return None
        obj = self._get_avatar_obj(obj)
        if not obj:
            return None
        return func(self, obj)

    return wrapper


class AvatarAdmin:
    """
        Use this class for showing avatar image and icon for some models
    """
    avatar_field = "avatar"

    def _get_avatar_obj(self, obj):
        return obj

    @admin_display(description=_("icon"))
    @avatar_wrapper
    def avatar_icon(self, obj=None):
        """
            Show avatar icon
        """
        return get_edit_icon(obj, image_field=self.avatar_field)

    @admin_display(description=_("image"))
    @avatar_wrapper
    def avatar_image(self, obj=None):
        """
            Show avatar image
        """
        return get_avatar_image(getattr(obj, self.avatar_field),
                                title=str(obj), link=get_edit_url(obj))


class PrettyJsonAdmin:
    """
        Use this class for showing pretty json data in admin panel object page
    """
    DATA_FIELD = "data"

    def _get_json_data(self, obj):
        return getattr(obj, self.DATA_FIELD, None)

    @admin_display(description=_("pretty data"))
    def pretty_data(self, obj=None):
        """
            Get pretty html component and use in object admin panel
        """
        if not obj:
            return None
        try:
            json_data = self._get_json_data(obj)
        except Exception as e:
            logger.error(e)
            return None
        return get_pretty_json(json_data)


class AbstractEditorAdmin:
    """
        Use this class for all models with editor and insert_dt and update_dt
    """

    def _handle_instance(self, obj):
        """
            For change extra field from inline object call this function
        """
        pass


class AdvanceSearchAdmin:
    """
        Use this class for add advance search option
    """

    change_list_template = 'admin/custom_change_list.html'
    search_form_data = None
    search_form = None

    def changelist_view(self, request, extra_context=None):
        """
            Add extra option
        """
        if self.search_form is not None:
            self.search_form_data = self.search_form(request.GET)
            extra_context = {'asf': self.search_form_data}
        # noinspection PyUnresolvedReferences
        return super().changelist_view(request, extra_context=extra_context)


class AdvanceListFilter:
    def get_list_filter(self, request):
        """
            Get list filter
        """
        list_filters = list(super().get_list_filter(request))
        obtained_list_filters = []
        for list_filter in list_filters:
            if type(list_filter) == tuple:
                name, filter_type = list_filter
                if filter_type == RelatedDropdownFilter:
                    obtained_list_filters.append((name, RelatedDropdownFilter))
                elif filter_type == CountRelatedDropdownFilter:
                    obtained_list_filters.append((name, CountRelatedDropdownFilter))
                elif filter_type == AutoCompleteFieldListFilter:
                    obtained_list_filters.append(AutocompleteFilterFactory(name.split("__")[-1], name))
                continue
            obtained_list_filters.append(list_filter)
        return obtained_list_filters
