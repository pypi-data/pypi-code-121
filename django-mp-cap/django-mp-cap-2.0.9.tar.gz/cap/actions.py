
from django import forms
from django.contrib import admin
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages


def related_field_change_action(model, field_name, action_name):

    class FieldForm(forms.Form):

        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

        value = forms.ModelChoiceField(
            label=model._meta.verbose_name,
            queryset=model.objects.all())

    def field_change_action(modeladmin, request, queryset):

        data = request.POST

        apply = 'apply' in data

        initial = {
            '_selected_action': data.getlist(admin.ACTION_CHECKBOX_NAME)
        }

        form = FieldForm(
            data=data if apply else None,
            initial=initial if not apply else None)

        if apply and form.is_valid():

            queryset.update(**{field_name: form.cleaned_data['value']})

            messages.success(request, _('Changes saved'))

            return redirect(request.get_full_path())

        context = admin.site.each_context(request)

        context.update({
            'items': queryset,
            'form': form,
            'action_name': 'field_change_action'
        })

        return render(
            request,
            'admin/change_related_field_action.html',
            context)

    field_change_action.short_description = action_name

    return field_change_action
