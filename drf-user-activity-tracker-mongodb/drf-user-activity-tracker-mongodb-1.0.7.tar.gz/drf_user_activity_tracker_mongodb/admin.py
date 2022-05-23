from django.contrib import admin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib import messages
from drf_user_activity_tracker_mongodb.utils import (MyCollection,
                                                     get_all_url_names,
                                                     ParamsHandler)
from drf_user_activity_tracker_mongodb.utils import database_log_enabled

if database_log_enabled():
    from drf_user_activity_tracker_mongodb.models import ActivityLog


    @admin.register(ActivityLog)
    class ActivityLogAdmin(admin.ModelAdmin):
        model = ActivityLog

        def get_urls(self):
            info = self.model._meta.app_label, self.model._meta.model_name
            print('%s_%s_changelist' % info)

            return [
                path(r'', self.admin_site.admin_view(self.activity_log_view), name='%s_%s_changelist' % info),
                path(r'<str:pk>/change/',
                     self.admin_site.admin_view(self.activity_log_detail_view),
                     name='%s_%s_change' % info)
            ]

        def activity_log_view(self, request):
            params = ParamsHandler(request)

            url_names_list = get_all_url_names()
            url_name = params.get_url_name()
            search_value = params.get_search_value()
            status_code = params.get_status()
            time_delta = params.get_time_delta()

            page = request.GET.get('page', 1)

            dataset = MyCollection().list(url_name=url_name, user_id=search_value, status_code=status_code,
                                          time_delta=time_delta)
            paginator = Paginator(dataset, 50)

            try:
                page_object = paginator.page(page)
            except PageNotAnInteger:
                page_object = paginator.page(1)
            except EmptyPage:
                page_object = paginator.page(paginator.num_pages)

            context = dict(self.admin_site.each_context(request), dataset=page_object, url_names=url_names_list,
                           count=paginator.count)
            return TemplateResponse(request, "activity_log/admin/change_list.html", context=context)

        def activity_log_detail_view(self, request, pk=None):
            data = MyCollection().detail(pk)
            if not data:
                messages.warning(request, f"Log with ID '{pk}' doesn’t exist. Perhaps it was deleted?")
                return redirect(reverse('admin:index'))
            context = dict(self.admin_site.each_context(request), data=data)
            return TemplateResponse(request, "activity_log/admin/change_detail.html", context=context)
