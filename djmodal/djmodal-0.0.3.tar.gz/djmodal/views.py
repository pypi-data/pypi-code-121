
from django.views.generic import FormView
from django.http.response import JsonResponse


class PopupFormView(FormView):

    error_status_code = 403
    success_response_class = JsonResponse

    def form_valid(self, form):
        obj = self.save_form(form)
        return self.success_response_class(self.get_success_context(obj))

    def save_form(self, form):
        return form.save()

    def get_success_context(self, obj):
        return {}

    def form_invalid(self, form):
        return self.render_to_response(
            {
                'content_only': True,
                **self.get_context_data(form=form)
            },
            status=403
        )
