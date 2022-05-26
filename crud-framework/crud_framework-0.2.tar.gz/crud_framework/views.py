from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from furl import furl
from django.views.generic import View
from json import loads as unjsonize
from .errors import Error


def my_furl(url):
    args = furl(url=url).args
    res = {}
    for k in args.keys():
        vs = args.allvalues(k)
        res[k] = vs if len(vs) > 1 else vs[0]
    return res


def view_catch_error(f):
    def wrap(request, *args, **kwargs):
        try:
            print(request.build_absolute_uri())
            try:
                filters = my_furl(request.build_absolute_uri())
            except:
                filters = {}
            # logged_in_user = get_user(request)  # TODO

            return f(request=request, filters=filters)
        except Error as e:
            return JsonResponse(status=e.status, data=dict(e))

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


@method_decorator([csrf_exempt, view_catch_error], name='dispatch')
class CrudView(View):
    CRUD_CLASS = None

    @classmethod
    def get_path(cls):
        return cls.CRUD_CLASS.PATH

    @classmethod
    def get_route_kwargs(cls):
        return dict(route=cls.get_path(), view=cls.as_view(), name=cls.CRUD_CLASS.__name__)

    # TODO filters for class not per function
    # TODO handle foreign key
    def _respond(self):
        if self.data:
            return JsonResponse(status=201, data=self.data, safe=False)
        else:
            return JsonResponse(status=204, data=[], safe=False)

    def get(self, request, filters):
        crud = self.CRUD_CLASS(filters)
        self.data = crud.get()
        return self._respond()

    def post(self, request, filters):
        print('in post')
        crud = self.CRUD_CLASS(filters)
        body = unjsonize(request.body.decode())
        self.data = crud.post(body)
        return self._respond()

    def bulk_post(self, request, filters):
        crud = self.CRUD_CLASS(filters=filters)
        body = unjsonize(request.body.decode())
        self.data = crud.bulk_post(body)
        return self._respond()

    def put(self, request, filters):
        crud = self.CRUD_CLASS(filters)
        body = unjsonize(request.body.decode())
        self.data = crud.put(body)
        return self._respond()

    def delete(self, request, filters):
        crud = self.CRUD_CLASS(filters)
        if not crud.delete():
            return HttpResponse(status=404)
        return self._respond()

    @classmethod
    def get_doc(cls, request):
        crud = cls.CRUD_CLASS({})
        return render(request, crud.template_path)
