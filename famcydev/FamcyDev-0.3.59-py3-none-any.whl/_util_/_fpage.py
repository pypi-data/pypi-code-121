from Famcy._util_._fwidget import FamcyWidget
from Famcy._util_._flayout import *
from Famcy._util_._fsubmission import *
from Famcy._util_._fpermissions import *
from Famcy._util_._fthread import *
from flask import g, Response, request, session, redirect, url_for
from flask_login import login_required
import Famcy
import time
import abc
import pickle
import os
import sys
import threading

class FPage(FamcyWidget):
	"""
	This page represents each of the page 
	on Famcy. It handles rendering, layout, 
	submission, etc... providing an overview
	of everything that happens in the page. 

	Routing of the page is defined by the folder
	/ subfolders file structure. 

	Abstraction:
		AF(route, style) = The page that is at url route and 
		apply css / js style of style
	
	Rep:
		* layout: FamcyLayout. Represent the layout
		of Famcy cards of the page. 
		* permission: FPermissions. Represent
		the allowed access of the user to this page. 

	Interface:
		* render(): render the page
		* register(): register the page to the Famcy env
		* preload(): action before the rendering
		* postload(): actions after the rendering
	"""
	route = "/"
	style = None
	permission = None
	background_thread_flag = False
	background_freq = 0.5
	event_source_flag=False
	_lock = threading.Lock()

	def __init__(self, layout_mode=FLayoutMode.recommend):
		super(FPage, self).__init__()
		self.layout = FamcyLayout(self, layout_mode, page_parent=self)

		self.submission_obj = FSubmission(self)
		self.submission_obj_key = self.id

		self.init_page()

		if self.background_thread_flag:
			self.sijax_response = None

			route_list = self.route[1:].split("/")
			route_name = '_'.join(route_list)
			session[route_name+"BackgroundQueueDict"] = FamcyPriorityQueue()

			# Check loop correctness
			assert getattr(self, "background_thread_inner", None), "Must implement background_thread_inner"
			# self.bthread = FamcyThread(target=self.background_thread_loop, daemon=True)
			# self.bthread.start()

		self._check_rep()

	def __getstate__(self):
		# handle pickle error
		# Developers cannot access bthread
		rv = self.__dict__.copy()
		return rv

	def init_page(self):
		self.body = Famcy.ELEMENT()

	def _check_rep(self):
		"""
		Check rep invariant:
			- Famcy layout in bound
			- Permission is not empty, able to 
				access in some way. 
		"""
		pass

	# def set_cookie(self, key, value):
	# 	session[key] = value

	# def get_cookie(self, key):
	# 	return session.get(key)

	@classmethod
	def setClassAttr(cls, key, value):
		if key in cls.__dict__.keys():
			cls.__dict__[key] = value

	@classmethod
	def register(cls, route, style, permission_level=0, background_thread=False, background_freq=0.5, init_cls=None, event_source_flag=False):
		cls.route = route
		cls.style = style
		cls.permission = FPermissions(permission_level)
		cls.background_thread_flag = background_thread
		cls.background_freq = background_freq
		cls.event_source_flag = event_source_flag

		route_func = lambda: cls.render(init_cls=init_cls)
		route_func.__name__ = "famcy_route_func_name"+route.replace("/", "_")

		selected_blueprint = Famcy.PageBlueprint if cls.style._sijax_enable else Famcy.MainBlueprint
		if cls.permission.required_login():
			# Register the page render to the main blueprint
			Famcy.FManager["flask_sijax"].route(selected_blueprint, cls.route)(login_required(route_func))
		else:
			Famcy.FManager["flask_sijax"].route(selected_blueprint, cls.route)(route_func)

		if cls.background_thread_flag:
			bg_func = lambda: cls.background_generator_loop()
			bg_func.__name__ = "bgloop_famcy_route_func_name"+route.replace("/", "_")

			if cls.permission.required_login():
				# Register the page render to the main blueprint
				Famcy.FManager["BgBlueprint"].route(cls.route+"/bgloop")(login_required(bg_func))
			else:
				Famcy.FManager["BgBlueprint"].route(cls.route+"/bgloop")(bg_func)

	@staticmethod
	def get_request_args(key_name):
		return request.args.get(key_name)

	@classmethod
	def render(cls, init_cls=None, *args, **kwargs):
		session["login_route"] = ""
		route_list = request.path[1:].split("/")
		route_name = '_'.join(route_list)

		if cls.style._sijax_enable and request.method == 'POST' and g.sijax.is_sijax_request:
			## Only POST and sijax enable request can enter here
			FSubmissionSijaxHandler.current_page = session.get(route_name+'current_page')

			g.sijax.register_object(FSubmissionSijaxHandler)

			# code for upload form
			upload_list = session.get(route_name+'current_page').find_class(session.get(route_name+'current_page'), "upload_form")
			for _item in upload_list:
				attribute = getattr(FSubmissionSijaxHandler, "upload_form_handler")
				_ = g.sijax.register_upload_callback(_item.id, attribute)

			sijax_res = g.sijax.process_request()

			return sijax_res

		# init page
		if request.method == 'GET':
			if init_cls:
				current_page = init_cls
			else:
				if route_name+"current_page" in session.keys():
					if route_name+"BackgroundQueueDict" in session.keys():
						del session[route_name+"BackgroundQueueDict"]
					del session[route_name+"current_page"]

				# reset Famcy widget id
				FamcyWidget.reset_id()
				current_page = cls()

			if not isinstance(cls.style, Famcy.VideoStreamStyle):
				print(route_name + "___ Save to session current_page")
				session[route_name+"current_page"] = current_page

		elif request.method == 'POST':
			if session[route_name+"current_page"]:
				current_page = session[route_name+"current_page"]
			else:
				print("POST didn't receive anything *************")
				return ""

		form_init_js = ''	# no use
		end_script = ''
		if not current_page.permission.verify(Famcy.FManager["CurrentUser"]):
			session["login_permission"] = "You are not authorized to view this page!"
			session["login_route"] = request.path

			return redirect(url_for("PageBlueprint.famcy_route_func_name_"+Famcy.FManager["ConsoleConfig"]['login_url'].replace("/", "_"), next=request.path.replace("/", " ")))
		else:
			# Render all content
			current_page.body = super(FPage, current_page).render()
			content_data = current_page.body.render_inner()
			head_script, end_script = current_page.body.render_script()
			for temp, _ in current_page.layout.staticContent:
				h_s, e_s = temp.body.render_script()
				head_script += h_s
				end_script += e_s

			# Apply style at the end
			return current_page.style.render(current_page.header_script+head_script, content_data, event_source_flag=current_page.event_source_flag, background_flag=current_page.background_thread_flag, route=current_page.route, time=int(1/current_page.background_freq)*1000, form_init_js=form_init_js, end_script=end_script)
		return ""

	@staticmethod
	def background_generator_loop():
		route_list = request.path[1:].split("/")
		del route_list[-1]
		route_name = '_'.join(route_list)

		_page = session.get(route_name+'current_page')
		_page.background_thread_inner()
		session[route_name+'current_page'] = _page

		try:
			baction = session.get(route_name+'BackgroundQueueDict').pop()
			indicator = True
			message = baction.tojson()

		except Exception as e:
			indicator = False
			message = str(e)

		def generate():
			yield json.dumps({"indicator": indicator, "message": message})

		
		return Response(generate(), mimetype='text/plain')

	def background_thread_inner(self):
		"""
		This is the background thread
		inner content for fpage. 
		"""
		pass

	# Functions that can be overwritten
	# ---------------------------------
	def render_inner(self):
		"""
		This is the function to 
		render the layout. 
		"""
		header_script, self.body = self.layout.render()

		if header_script not in self.header_script:
			self.header_script += header_script
		
		return self.body

	def preload(self):
		"""
		This is the preload function
		that should be executed before 
		the inner render function. 
		"""
		pass

	def postload(self):
		"""
		After the page is rendered, 
		apply async post load function. 
		"""
		pass

