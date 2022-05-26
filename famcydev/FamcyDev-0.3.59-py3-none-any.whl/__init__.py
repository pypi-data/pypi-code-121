# -*- coding: UTF-8 -*-
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, abort, current_app, Blueprint, send_from_directory, g, Response, stream_with_context
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
import flask_sijax
import sijax
from flask_sse import sse
import redis
from flask_kvsession import KVSessionExtension, KVSessionInterface
from simplekv.memory.redisstore import RedisStore

import os
import importlib
import Famcy
import json
import time
import random
import dill
import pickle
import base64
import threading
import copy

from Famcy._util_._fmanager import *
from Famcy._util_._fauth import *
from Famcy._util_._felement import *
from Famcy._util_._fblock import *
from Famcy._util_._fpage import *
from Famcy._util_._fcard import *
from Famcy._util_._flayout import *
from Famcy._util_._fstyle import *
from Famcy._util_._fpermissions import *
from Famcy._util_._fthread import *
from Famcy._util_._flayout import *
from Famcy._util_._fstyle import *
from Famcy._util_._fsubmission import *

__codename__ = "Xinhai"
famcy_dir = os.path.dirname(Famcy.__file__)

# Create Global Var for User usage
FamcyElement = FElement
FamcyBlock = FBlock
FamcyPage = FPage
FamcyCard = FCard
FamcyPermissions = FPermissions
FamcyInputBlock = FInputBlock
FamcyUploadBlock = FUploadBlock
FamcyPromptCard = FPromptCard
FamcyResponse = FResponse
FamcyPriority = FPriority

# Login Related
FamcyUser = FUser
FamcyLogin = FLogin
FamcyLoginManager = None

# Layout Related
FamcyLayoutMode = FLayoutMode

# Style Related
FamcyStyle = FStyle
FamcyStyleLoader = FStyleLoader
FamcyColorTheme = FColorTheme
FamcyFontTheme = FFontTheme
FamcyStyleSideBar = FStyleSideBar
FamcyStyleSideBtns = FStyleSideBtns
FamcyStyleNavBar = FStyleNavBar
FamcyStyleNavBtns = FStyleNavBtns
FamcyBackgroundTask = FBackgroundTask


class famcy_sijax(flask_sijax.Sijax):
	def __init__(self):
		super(famcy_sijax, self).__init__()

	def init_app(self, app, blueprints):
		"""
		app: flask app
		blueprint: a list of blueprints that
		need to add the sijax function
		"""
		for b in blueprints:
			b.before_request(self._on_before_request)

		static_path = app.config.get('SIJAX_STATIC_PATH', None)
		if static_path is not None:
			sijax.helper.init_static_path(static_path)

		self._json_uri = app.config.get('SIJAX_JSON_URI', None)

		app.extensions = getattr(app, 'extensions', {})
		app.extensions['sijax'] = self
		
	def _on_before_request(self):
		# print("========================_on_before_request========================", request)
		# Famcy.sem.acquire()
		_r_form = copy.deepcopy(request.form)
		_r_host_url = copy.deepcopy(request.host_url)
		_r_url = copy.deepcopy(request.url)
		g.sijax = self
		g.route_path = request.path
		
		self._sijax = sijax.Sijax()
		self._sijax.set_data(_r_form)

		url_relative = _r_url[len(_r_host_url) - 1:]
		self._sijax.set_request_uri(url_relative)

		# print("url_relative: ", url_relative)

		if self._json_uri is not None:
			self._sijax.set_json_uri(self._json_uri)
		# Famcy.sem.release()
		

def create_app(famcy_id, production=False):
	"""
	Main creation function of the famcy application. 
	Can set to different factory settings in the future. 
	"""
	# Famcy Manager that manage all global vars, imports, 
	# file systems, http
	FManager = FamcyManager(famcy_id, famcy_dir, production=production)
	globals()["FManager"] = FManager

	# Header definitions
	FManager["CUSTOM_STATIC_PATH"] = FManager.console + "_static_"

	# Sijax, submission related
	FManager["flask_sijax"] = flask_sijax
	FManager["Sijax"] = famcy_sijax()
	# FManager["SijaxSubmit"] = SubmitType
	FManager["SijaxStaticPath"] = FManager.main + 'static/js/sijax/'
	FManager["SijaxJsonUri"] = '/static/js/sijax/json2.js'

	# User, login related init
	FManager["FamcyUser"] = FUser
	FManager["LoginManager"] = LoginManager()
	FManager["CurrentUser"] = current_user
	FManager["CurrentApp"] = current_app

	# System Wide blueprints and application object
	MainBlueprint = Blueprint('MainBlueprint', __name__)
	globals()["MainBlueprint"] = MainBlueprint
	FManager["MainBlueprint"] = MainBlueprint

	# System Wide page blueprints w/ sijax
	PageBlueprint = Blueprint('PageBlueprint', __name__)
	globals()["PageBlueprint"] = PageBlueprint
	FManager["PageBlueprint"] = PageBlueprint

	# System Wide bgloop blueprints
	BgBlueprint = Blueprint('BgBlueprint', __name__)
	globals()["BgBlueprint"] = BgBlueprint
	FManager["BgBlueprint"] = BgBlueprint

	# Webpage related configs
	FManager["ConsoleConfig"] = FManager.read(FManager.console + "/famcy.yaml")

	if "lg_yaml" in FManager["ConsoleConfig"].keys():
		FManager.lg_yaml = FManager.read(FManager["ConsoleConfig"]["lg_yaml"])

	# ------------------------
	# --- Main app start zone
	# ------------------------
	app = Flask(__name__)
	globals()["app"] = app
	# Some sort of security here -> TODO check on this
	app.config['SECRET_KEY'] = FManager.get_credentials("flask_secret_key", "").encode("utf-8")

	# Init Sijax
	FManager["Sijax"].init_app(app, [PageBlueprint])
	FamcyBackgroundQueue = FamcyPageQueue()
	globals()["FamcyBackgroundQueue"] = FamcyBackgroundQueue

	# Init http client
	FManager.init_http_client(**FManager["ConsoleConfig"])
	# Security Enhance
	FManager.register_csrf(app)

	# redis server
	r = redis.StrictRedis()

	store = RedisStore(r)
	globals()["store"] = store
	if "serialization_method" in FManager["ConsoleConfig"].keys() and FManager["ConsoleConfig"]["serialization_method"] == "dill":
		KVSessionInterface.serialization_method = dill
	else:
		KVSessionInterface.serialization_method = pickle
	KVSessionExtension(store, app)

	# event based
	app.config["REDIS_URL"] = "redis://localhost"
	globals()["sse"] = sse
	FManager["sse"] = sse
	app.register_blueprint(sse, url_prefix="/event_source")

	# avoid multiple thread race condition issue
	sem = threading.Semaphore()
	globals()["sem"] = sem

	# ros2
	FManager.ros2_init()

	# User Static Data
	@MainBlueprint.route('/asset/<path:filename>')
	def user_custom_asset(filename):
		return send_from_directory(FManager.console + "/" + FManager.USER_STATIC_FOLDER, filename)

	# Import Fblocks from default and custom folders. 
	# ------------------------------
	# Get all sources of felements definitions 
	system_styles = FManager.importclassdir(FManager.main + "/", "_elements_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_styles)

	# Get all sources of fblocks definitions 
	system_items = FManager.importclassdir(FManager.main + "/", "_items_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_items)

	# Get all sources of fresponse definitions 
	system_responses = FManager.importclassdir(FManager.main + "/", "_responses_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_responses)

	# Get all sources of fstyle definitions 
	system_styles = FManager.importclassdir(FManager.main + "/", "_style_", FamcyFileImportMode.name, "", 
		exclude=["_", "."], otherwise=[], recursive=True)
	FManager.assign_to_global(globals(), system_styles)

	# Import module recursively for all pages in the console folder
	class_dir = FManager.importclassdir(FManager.console, "", FamcyFileImportMode.fixed, "page", recursive=True, 
			exclude=["_", "."], otherwise=None)

	# Register the main blueprint that is used in the FamcyPage
	app.register_blueprint(MainBlueprint)

	# Register the page blueprint that uses sijax
	app.register_blueprint(PageBlueprint)

	# Register the bg blueprint
	app.register_blueprint(BgBlueprint)

	# Init Login Manager and Related Stuffs
	if FManager["ConsoleConfig"]["with_login"]:
		# Init login manager
		r = FManager["ConsoleConfig"]['login_url'].replace("/", "_")[1:] if FManager["ConsoleConfig"]['login_url'].replace("/", "_")[0] == "/" else FManager["ConsoleConfig"]['login_url'].replace("/", "_")
		FManager["LoginManager"].login_view = "PageBlueprint.famcy_route_func_name_"+r
		FManager["LoginManager"].init_app(app)
		FManager["FamcyUser"].setup_user_loader()
		assert Famcy.FamcyLoginManager, "User Must Register Famcy Login Manager"

	return app

# ------ above is the flask part -----------
