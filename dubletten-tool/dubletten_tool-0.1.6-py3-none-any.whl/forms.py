from django.forms import ModelForm, HiddenInput
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, Submit
from .models import Group, PersonProxy

class GroupForm(ModelForm):
    class Meta: 
        model = Group
        fields = ("note",)

    def __init__(self, inst_id, *args, **kwargs):
        super(GroupForm, self).__init__( *args, **kwargs)

        print("in Group Form, inst_id", inst_id)
        print("args:", args)
        print("kwargs:", kwargs)
        #self.fields['id'].widget = HiddenInput()
        #self.fields['id'].initial = inst_id

        self.helper = FormHelper()
        self.helper.form_class = "NoteForm"
        self.helper.form_tag = True
        self.helper.help_text_inline = True
        self.helper.form_action = reverse("dubletten_tool:handle_note_form", kwargs={"g_id":inst_id, "type":"group"})
        self.helper.add_input(Submit("submit", "save", css_id=f"post_note_{inst_id}"))
        self.helper.add_input(Button("cancel", "Cancel", css_class="btn-danger", onclick=f"abortNoteEdit({inst_id},'group')"))
        print(self.fields)
        #self.helper.layout = Layout("id", "note")



class PersonProxyForm(ModelForm):
    class Meta: 
        model = PersonProxy
        fields = ["note"]

    def __init__(self, inst_id, *args, **kwargs):
        super(PersonProxyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "NoteForm"
        self.helper.form_tag = True
        self.helper.help_text_inline = True
        self.helper.form_action = reverse("dubletten_tool:handle_note_form", kwargs={"g_id":inst_id, "type":"personproxy"})
        self.helper.add_input(Submit("submit", "save", css_id=f"post_note_{inst_id}"))
        self.helper.add_input(Button("cancel", "Cancel", css_class="btn-danger", onclick=f"abortNoteEdit({inst_id},'personproxy')"))

    


    