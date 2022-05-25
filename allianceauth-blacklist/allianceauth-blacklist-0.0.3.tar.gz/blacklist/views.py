from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from .models import EveNote, EveNoteComment
from .forms import EveNoteForm, AddComment
from django.http import HttpResponse
from django.template.loader import render_to_string
from . import providers

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)

# Create your views here... *don't tell me what to do....*


@login_required
def note_board(request):
    add_perms = request.user.has_perm('blacklist.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('blacklist.add_new_eve_notes')
    add_blacklist_perms = request.user.has_perm('blacklist.add_to_blacklist')
    add_restricted_perms = request.user.has_perm('blacklist.add_restricted_eve_notes')
    view_perms = request.user.has_perm('blacklist.view_basic_eve_notes')
    view_global_perms = request.user.has_perm('blacklist.view_eve_notes')

    if not (view_perms or view_global_perms):
        messages.error(request, "No Permissions")
        return redirect('authentication:dashboard')

    eve_notes = None

    if view_global_perms or add_global_perms:
        eve_notes = EveNote.objects.filter(restricted=False
                                           ).prefetch_related('comment')
        #  Restricted view
        if add_restricted_perms:
            if eve_notes:
                eve_notes = eve_notes | EveNote.objects.filter(restricted=True).prefetch_related('comment')
            else:
                eve_notes = EveNote.objects.filter(restricted=True).prefetch_related('comment')

    else:
        #  Basic Level
        eve_notes = EveNote.objects.filter(corporation_id=request.user.profile.main_character.corporation_id,
                                           restricted=False).prefetch_related('comment')

    context = {
        'add_note': (add_perms or add_global_perms),
        'view_restricted_note': request.user.has_perm('blacklist.view_restricted_eve_notes'),
        'add_blacklist': add_blacklist_perms,
        'edit_note': add_global_perms,
        'add_comment': request.user.has_perm('blacklist.add_new_eve_note_comments'),
        'add_restricted_comment': request.user.has_perm('blacklist.add_new_eve_note_restricted_comments'),
        'view_comment': request.user.has_perm('blacklist.view_eve_note_comments'),
        'view_restricted_comment': request.user.has_perm('blacklist.view_eve_note_restricted_comments'),
        'notes': eve_notes
    }

    return render(request, 'blacklist/evenotes.html', context=context)


@login_required
@permission_required('blacklist.view_eve_blacklist')
def blacklist(request):
    blacklist = EveNote.objects.filter(blacklisted=True)
    add_restricted_perms = request.user.has_perm('blacklist.add_restricted_eve_notes')

    context = {
        'blacklist': blacklist,
        'view_restricted_note': add_restricted_perms
    }

    return render(request, 'blacklist/blacklist.html', context=context)


@login_required
@permission_required('blacklist.add_new_eve_note_comments')
def get_evenote_comments(request, evenote_id=None):
    view_restricted = request.user.has_perm('view_eve_note_restricted_comments')
    comments = EveNote.objects.prefetch_related('comment').get(id=evenote_id).comment.all()
    if not view_restricted:
        comments = comments.filter(restricted=False)
    ctx = {
        'comments': comments,
        'add_blacklist': request.user.has_perm('blacklist.add_to_blacklist'),
        'add_restricted_note': request.user.has_perm('blacklist.add_restricted_eve_notes')

    }
    return HttpResponse(render_to_string('blacklist/modal_comments.html', ctx, request=request))


@login_required
@permission_required('blacklist.add_new_eve_notes')
def get_edit_evenote(request, evenote_id=None):
    note = EveNote.objects.get(id=evenote_id)
    ctx = {
        'note': note,
        'add_blacklist': request.user.has_perm('blacklist.add_to_blacklist'),
        'add_restricted_note': request.user.has_perm('blacklist.add_restricted_eve_notes')

    }
    return HttpResponse(render_to_string('blacklist/modal_edit_note.html', ctx, request=request))


@login_required
@permission_required('blacklist.add_new_eve_note_comments')
def get_add_comment(request, evenote_id=None):
    note = EveNote.objects.get(id=evenote_id)
    ctx = {
        'note': note,
        'add_restricted_note': request.user.has_perm('blacklist.add_new_eve_note_restricted_comments')

    }
    return HttpResponse(render_to_string('blacklist/modal_add_comment.html', ctx, request=request))


@login_required
@permission_required('blacklist.add_new_eve_notes')
def get_add_evenote(request, eve_id=None):
    add_perms = request.user.has_perm('blacklist.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('blacklist.add_new_eve_notes')
    add_blacklist_perms = request.user.has_perm('blacklist.add_to_blacklist')
    add_restricted_perms = request.user.has_perm('blacklist.add_restricted_eve_notes')
    message = None
    if not (add_perms or add_global_perms):
        message = "No Permissions"
        eve_id = None

    if eve_id:
        if request.method == 'POST':
            try:
                name = providers.esi.client.Universe.post_universe_names(ids=[eve_id]).result()[0]
                char_info = None
                corp_info = None
                alliance_info = None

                if name.get('category') == 'character':
                    char_info = providers.esi.client.Character.get_characters_character_id(character_id=eve_id).result()
                    corp_info = providers.esi.client.Corporation.get_corporations_corporation_id(
                        corporation_id=char_info.get('corporation_id')).result()
                    if corp_info.get('alliance_id', False):
                        alliance_info = providers.esi.client.Alliance.get_alliances_alliance_id(
                            alliance_id=corp_info.get('alliance_id')).result()

                elif name.get('category') == 'corporation':
                    corp_info = providers.esi.client.Corporation.get_corporations_corporation_id(
                        corporation_id=eve_id).result()
                    if corp_info.get('alliance_id', False):
                        alliance_info = providers.esi.client.Alliance.get_alliances_alliance_id(
                            alliance_id=corp_info.get('alliance_id')).result()

                if not add_global_perms:
                    if not (name.get('category') == 'character'):
                        message = "You can only add people from your own corp, Please contact a Diplo to add this note."
                    else:
                        if not int(request.user.profile.main_character.corporation_id) == int(char_info.get('corporation_id')):
                            message = "You can only add people from your own corp, Please contact a Diplo to add this note."

                if not message:
                    form = EveNoteForm()

                    context = {'form': form,
                               'name': name,
                               'char_info': char_info,
                               'corp_info': corp_info,
                               'alliance_info': alliance_info,
                               'add_blacklist': add_blacklist_perms,
                               'add_restricted_note': add_restricted_perms}
                    return HttpResponse(render_to_string('blacklist/add_note.html', context, request=request))

            except Exception as e:
                logger.error(e)
                message = e.message

    context = {'names': False,
               'searched': False,
               'message': message,
               'restricted_perms': add_global_perms
               }
    return HttpResponse(render_to_string('blacklist/search_name.html', context, request=request))


@login_required
def search_names(request):
    add_perms = request.user.has_perm('blacklist.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('blacklist.add_new_eve_notes')
    add_blacklist_perms = request.user.has_perm('blacklist.add_to_blacklist')
    add_restricted_perms = request.user.has_perm('blacklist.add_restricted_eve_notes')

    if not (add_perms or add_global_perms):
        messages.info(request, "No Permissions")
        return redirect('blacklist:note_board')
    names = None
    searched = False
    message = False
    if request.method == 'POST':
        # check whether it's valid:
        name = request.POST.get('name')
        try:
            hits = providers.esi.client.Search.get_search(
                search=name, categories=['character', 'corporation', 'alliance']).result()
            corps = hits.get('corporation', [])
            chars = hits.get('character', [])
            alliance = hits.get('alliance', [])
            names_list = []
            if corps:
                names_list += corps
            if chars:
                names_list += chars
            if alliance:
                names_list += alliance
            if len(names_list) > 0:
                names = providers.esi.client.Universe.post_universe_names(ids=names_list).result()
            searched = name
        except Exception as e:
            logger.error(e)
            message = e.message

    context = {'names': names,
               'searched': searched,
               'message': message,
               'restricted_perms': add_restricted_perms
               }
    return HttpResponse(render_to_string('blacklist/search_name.html', context, request=request))


@login_required
@permission_required('blacklist.add_new_eve_note_comments')
def add_comment(request, note_id=None):
    if request.method == 'POST':
        form = AddComment(request.POST)

        # check whether it's valid:
        if form.is_valid():
            restricted = form.cleaned_data['restricted']

            EveNoteComment.objects.create(added_by=request.user.profile.main_character.character_name,
                                          eve_note_id=note_id,
                                          comment=form.cleaned_data['comment'],
                                          restricted=restricted)
            messages.info(request, "Comment Added")
            return redirect('blacklist:note_board')
    else:
        form = AddComment()
        note = EveNote.objects.get(pk=note_id)
        context = {'form': form,
                   'note': note,
                   'add_restricted': request.user.has_perm('blacklist.add_new_eve_note_restricted_comments')}

        return render(request, 'blacklist/add_comment.html', context)


@login_required
def add_note(request, eve_id=None):
    add_perms = request.user.has_perm('blacklist.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('blacklist.add_new_eve_notes')

    if not (add_perms or add_global_perms):
        messages.info(request, "No Permissions")
        return redirect('blacklist:note_board')

    if eve_id:
        if request.method == 'POST':
            form = EveNoteForm(request.POST)

            # check whether it's valid:
            if form.is_valid():
                restricted = form.cleaned_data['restricted']

                blacklisted = form.cleaned_data['blacklisted']
                EveNote.objects.create(eve_name=request.POST.get('eve_name'),
                                       eve_catagory=request.POST.get('eve_cat'),
                                       alliance_id=request.POST.get('alliance_id', None),
                                       alliance_name=request.POST.get('alliance_name', None),
                                       corporation_id=request.POST.get('corporation_id', None),
                                       corporation_name=request.POST.get('corporation_name', None),
                                       blacklisted=blacklisted,
                                       restricted=restricted,
                                       reason=form.cleaned_data['reason'],
                                       added_by=request.user.profile.main_character.character_name,
                                       eve_id=eve_id)

                return redirect('blacklist:note_board')
    return redirect('blacklist:note_board')


@login_required
@permission_required('blacklist.add_new_eve_notes')
def edit_note(request, note_id=None):
    if request.method == 'POST':
        form = EveNoteForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            restricted = form.cleaned_data['restricted']
            blacklisted = form.cleaned_data['blacklisted']
            jb = EveNote.objects.get(id=request.POST.get('note_id'))
            jb.reason = form.cleaned_data['reason']
            jb.blacklisted = blacklisted
            jb.restricted = restricted
            jb.save()
            messages.info(request, "Edit Successful")
            return redirect('blacklist:note_board')
    else:
        note = EveNote.objects.get(pk=note_id)
        form = EveNoteForm(initial={'reason': note.reason,
                                    'blacklisted': note.blacklisted,
                                    'restricted': note.restricted,
                                    'ultra_restricted': note.ultra_restricted})
        context = {'form': form,
                   'note': note,
                   'add_blacklist': request.user.has_perm('blacklist.add_to_blacklist')}

        return render(request, 'blacklist/edit_note.html', context)
