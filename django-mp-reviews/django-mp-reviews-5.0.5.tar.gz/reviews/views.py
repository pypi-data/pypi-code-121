
from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.generic import View, ListView
from django.utils.translation import ugettext_lazy as _
from django.core.mail import mail_managers
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from pagination import PaginationMixin

from reviews.models import Review
from reviews.forms import ReviewForm


class ReviewListView(PaginationMixin, ListView):

    queryset = Review.objects.filter(is_active=True)
    paginate_by = 10
    template_name = 'reviews/list.html'


class ReviewAPI(View):

    def get(self, request, *args, **kwargs):
        context = {'form': ReviewForm()}
        return render(request, 'reviews/new_review_modal.html', context)

    def post(self, request, *args, **kwargs):

        form = ReviewForm(data=request.POST, files=request.FILES)

        if form.is_valid():

            review = form.save(commit=False)

            if request.user.is_authenticated:
                review.user = request.user

            review.answer = ''

            review.save()

            self._send_new_review_email(review)

            return HttpResponse(_('Review was successfully sent'))

        context = {'form': form}

        return render(
            request, 'reviews/new_review_form.html', context, status=400)

    def _send_new_review_email(self, review):

        subject = '{} #{}'.format(_('New review'), review.id)

        context = {'object': review, 'site': Site.objects.get_current()}

        html = render_to_string('reviews/new_review_email.html', context)

        mail_managers(
            subject=subject, message='', html_message=html, fail_silently=True
        )
