from django.urls import re_path
from . import views

app_name = 'blacklist'

urlpatterns = [
    re_path(r'^notes/$', views.note_board, name='note_board'),
    re_path(r'^blacklist/$', views.blacklist, name='blacklist'),
    re_path(r'^get_add_note/(?P<eve_id>(\d)*)/$', views.get_add_evenote, name='modal_add'),
    re_path(r'^get_comments/(?P<evenote_id>(\d)*)/$', views.get_evenote_comments, name='modal_comment'),
    re_path(r'^get_edit_note/(?P<evenote_id>(\d)*)/$', views.get_edit_evenote, name='modal_edit'),
    re_path(r'^get_add_comment/(?P<evenote_id>(\d)*)/$', views.get_add_comment, name='modal_add_comment'),
    re_path(r'^search_names/$', views.search_names, name='search_names'),
    re_path(r'^add_comment/(?P<note_id>(\d)*)/$', views.add_comment, name='add_comment'),
    re_path(r'^add_note/(?P<eve_id>(\d)*)/$', views.add_note, name='add_note'),
    re_path(r'^edit_note/(?P<note_id>(\d)*)/$', views.edit_note, name='edit_note'),
]
