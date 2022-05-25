from django.urls import path
from django.conf.urls import url
from .views import get_all_notes, getToolPage, getNoteJSON, HandleNoteForm, get_group_suggestions, get_group_ajax, rename_group, update_group_checkboxes, create_new_group, merge_groups, remove_member, get_singles, get_groups, get_single_ajax, get_person_suggestions
from .detail_view import OverwrittenGenericEntitiesDetailView
app_name = "dubletten_tool"

urlpatterns = [
    path("start/", getToolPage.as_view(), name="tool_page"),
    path("create_group/", create_new_group, name="create_new_group"),
    url(r"^handle_note_form/(?P<g_id>[0-9]+)/(?P<type>[a-z]+)/$", HandleNoteForm.as_view(), name="handle_note_form"),
    path("get_singles/", get_singles, name="get_singles"),
    path("get_all_notes/", get_all_notes, name="get_all_notes"),
    url(r"^get_single_ajax/(?P<s_id>[0-9]+)/$", get_single_ajax, name="get_single_ajax"),
    #url(r"^get_singles/(?P<val>[a-zA-Zäöüß#\-\_()]+)/(?P<type>[a-zA-Zäöüß#\_\-]+)/$", get_singles, name="get_singles"),
    url(r"^get_singles/(?P<val_name>[a-zA-Zäöüß#\-\_()]+)/(?P<val_first>[a-zA-Zäöüß#\_\-]+)/(?P<gender>[A-Za-z]+)/$", get_singles, name="get_singles"),
    url(r"^get_groups/(?P<val>[a-zA-Zäüöß_,\[\]\(\).]+)/(?P<gender>[A-Za-z]+)/$", get_groups, name="get_groups"),
    url(r"get_note_json/(?P<inst_id>[0-9]+)/(?P<type>[a-z]+)/$", getNoteJSON, name="get_note_json"),
    path("merge_groups/", merge_groups, name="merge_groups"),
    path("rename_group/", rename_group, name="rename_group"),
    url(r"^update_group_checkboxes/(?P<btn_id>[0-9]+)/(?P<group_id>[0-9]+)/$", update_group_checkboxes, name="update_group_checkboxes"),
    url(r"^get_group/(?P<g_id>[0-9]+)/$", get_group_ajax, name="get_group_ajax"),
    url(r"^remove_member/(?P<group_id>[0-9]+)/(?P<per_id>[0-9]+)/$", remove_member, name="remove_member"),
    url(r"^get_person_detail/(?P<per_id>[0-9]+)/$", OverwrittenGenericEntitiesDetailView.as_view(), name="get_person_detail"),
    url(r"^get_person_suggestions/(?P<per_id>[0-9]+)/$", get_person_suggestions, name="get_person_suggestions"),
    url(r"^get_group_suggestions/(?P<group_id>[0-9]+)/$", get_group_suggestions, name="get_group_suggestions"),






]

update_group_checkboxes