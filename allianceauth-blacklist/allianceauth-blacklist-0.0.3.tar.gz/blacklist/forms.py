from django import forms


class EveNoteForm(forms.Form):
    reason = forms.CharField(label='Reason', widget=forms.Textarea(attrs={'class': 'form-control'}))
    blacklisted = forms.BooleanField(label='Blacklist', required=False,
                                     widget=forms.CheckboxInput(attrs={'class': 'form-check'}))
    restricted = forms.BooleanField(label='Restricted', required=False,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check'}))


class AddComment(forms.Form):
    comment = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'class': 'form-control'}))
    restricted = forms.BooleanField(label='Restricted', required=False,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check'}))
