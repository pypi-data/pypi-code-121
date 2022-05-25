from django import http
from typing import Optional
from .base import SubView

_known_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
def _options(allowed_methods):
	if 'OPTIONS' not in allowed_methods :
		allowed_methods += ['OPTIONS']
	response = http.HttpResponse()
	response['Allow'] = ', '.join(allowed_methods)
	response['Content-Length'] = '0'
	return response

class MethodView(SubView):
	'''
	Utilitiy class for implementing dispatch-by-method, similar to
	django.views.generic.View.

	TODO - document better

	Note - we intentionally don't accept url parameters 
	(ie. captured from a Router).
	Anything that needs to interpret url parameters should be a Router,
	in a routers.py file. 
	'''
	def auth(self, sub_request) -> Optional[http.HttpResponse]:
		'''
		Subclasses may override.
		Will be called before any http-method handler runs.
		You may return an HttpResponse to prevent further processing.

		Note - we do NOT recommend do any complex permission checks here.
		Instead, the parent Router should set permission flags (or 
		permission checking functions) on sub_request. In that case, we can
		check those flags/functions here, and so can our parent page (so it
		can determine whether or not to link to us).
		'''
		pass
				
	def __init__(self):
		methods = {}
		for method_name in _known_methods :
			try :
				# Note - self will NOT be passed to method, even if not declared as staticmethod
				methods[method_name] = getattr(self.__class__, method_name)
			except AttributeError :
				pass
		self._allowed_methods = [name.upper() for name in methods]
		self._methods = methods

		# Protect against two things:
		# 1. A method you intended to implement, but you had a typo in the name
		# 2. Habitually adding helper methods (used by multiple http methods) to subclasses (which might cause you to inadvertently implement an http method)
		for c in self.__class__.__mro__ :
			if c != MethodView :
				for key in c.__dict__ :
					if not key.startswith('_') and not key in _known_methods :
						raise AttributeError(f'Illegal attribute "{key}" on class {c}. The only attributes you may define on a MethodView subclass are standard HTTP methods.')

	def __call__(self, sub_request):
		early_response = self.auth(sub_request)
		if early_response :
			return early_response

		mname = sub_request.request.method.lower()
		try :
			method = self._methods[mname]
		except KeyError :
			if mname == 'options' :
				return _options(self._allowed_methods)
			return http.HttpResponseNotAllowed(self._allowed_methods)
		return method(sub_request)
