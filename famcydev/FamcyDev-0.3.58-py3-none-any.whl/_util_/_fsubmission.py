import abc
import enum
import json
import pickle
import time
import Famcy
import _ctypes
import os
import datetime
from flask import session, request, Response, g
from werkzeug.utils import secure_filename

# GLOBAL HELPER
def get_fsubmission_obj(parent, obj_id):
	""" Inverse of id() function. But only works if the object is not garbage collected"""
	if parent:
		return parent.find_obj_by_id(parent, obj_id)

def alert_response(info_dict, form_id):
		"""
		Template for generating alert response
		"""
		inner_text = '''
		<div class="alert %s" id="alert_msg_%s" role="alert">
			%s
		</div>
		''' % (info_dict["alert_type"], form_id, info_dict["alert_message"])

		extra_script = '''
		$("#alert_msg_%s").fadeTo(2000, 500).slideUp(500, function(){
			$("#alert_msg_%s").slideUp(500);
			$("#alert_msg_%s").remove();
		});
		''' % (form_id, form_id, form_id)

		return inner_text, extra_script

def exception_handler(func):
	"""
	This is the decorator to 
	assign the exception response
	when there is an exception.
	"""

	def inner_function(*args, **kwargs):
		try:
			func(*args, **kwargs)
		except:
			# # Arg1 is intend to be the submission id of the submission object
			# fsubmission_obj = get_fsubmission_obj(None, args[1])
			# inner_text, extra_script = alert_response({"alert_type":"alert-warning", "alert_message":"系統異常", "alert_position":"prepend"}, fsubmission_obj.origin.id)
			# # args[0] is the sijax response object
			# args[0].html_prepend('#'+fsubmission_obj.target.id, inner_text)
			# args[0].script(extra_script)
			# args[0].script("$('#loading_holder').css('display','none');")
			pass

	return inner_function

def put_submissions_to_list(fsubmission_obj, sub_dict):
	"""
	This is the helper function to put the
	submission content to a list of arguments
	- Input:
		* sub_dict: submission dictionary
	"""
	input_parent = fsubmission_obj.origin.find_parent(fsubmission_obj.origin, "input_form")
	f_submit_info = FSubmissionInfo()
	f_submit_info.info_list = []

	if input_parent:
		for child, _, _, _, _ in input_parent.layout.content:
			if child.name in sub_dict.keys():
				f_submit_info.info_dict[child.submit_value_name] = sub_dict[child.name][0] if len(sub_dict[child.name]) == 1 else sub_dict[child.name]
				f_submit_info.info_list.append(sub_dict[child.name])

	return f_submit_info

def allowed_file(filename, extension_list):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in extension_list

class FSubmissionInfo(object):
	def __init__(self):
		self.info_list = []
		self.info_dict = {}

	def __getitem__(self, item):
		if isinstance(item, int):
			if item < len(self.info_list):
				return self.info_list[item]
		else:
			if item in self.info_dict.keys():
				return self.info_dict[item]
		return None

	def __iter__(self):
		# list prioritized over dictionary
		if len(self.info_list) != 0:
			for info in self.info_list:
				yield info
				
		elif len(list(self.info_dict.keys())) != 0:
			for key in self.info_dict.keys():
				yield self.info_dict[key]

class FResponse(metaclass=abc.ABCMeta):
	def __init__(self, target=None):
		self.target = target
		self.finish_loading_script = "$('#loading_holder').css('display','none');"

	def run_all_script_tag(self, html, sijax_response):
		pure_html = ""

		def _find_script(_pure_html, _html):
			start = _html.find("<script>")
			_pure_html += _html[:start]
			if start > 0:
				end = _html.find("</script>")
				sijax_response.script(_html[start+8:end])
				return _pure_html, _html[end+9:]
			return _pure_html, False

		while html:
			pure_html, html = _find_script(pure_html, html)

		return pure_html


	@abc.abstractmethod
	def response(self, sijax_response):
		"""
		This is the function that gives
		response to the sijax input
		"""
		pass

class FSubmissionSijaxHandler(object):
	"""
	This is the sijax handler for
	handling the specific submission id
	and offer a response. 
	"""
	current_page = None

	@staticmethod
	# @exception_handler
	def famcy_submission_handler(obj_response, fsubmission_id, info_dict, **kwargs):
		"""
		This is the main submission handler that handles all
		the submission traffics. 
		"""
		print("========================== famcy_submission_handler ==========================")
		# Get the submission object
		fsubmission_obj = get_fsubmission_obj(FSubmissionSijaxHandler.current_page, fsubmission_id)
		if "jsAlert" in info_dict.keys():
			temp_func = fsubmission_obj.jsAlertHandler
			response_obj = temp_func(fsubmission_obj, info_dict)
		else:
			info_list = put_submissions_to_list(fsubmission_obj, info_dict)
			# Run user defined handle submission
			# Will assume all data ready at this point
			temp_func = fsubmission_obj.func
			response_obj = temp_func(fsubmission_obj, info_list)
		# print("temp_func: ", temp_func)

		# Response according to the return response
		if isinstance(response_obj, list):
			for res_obj in response_obj:
				res_obj.target = res_obj.target if res_obj.target else fsubmission_obj.target
				res_obj.response(obj_response)
		elif response_obj:
			response_obj.target = response_obj.target if response_obj.target else fsubmission_obj.target
			response_obj.response(obj_response)
		else:
			inner_text, extra_script = alert_response({"alert_type":"alert-warning", "alert_message":"系統異常", "alert_position":"prepend"}, fsubmission_obj.origin.id)
			# args[0] is the sijax response object
			obj_response.html_prepend('#'+fsubmission_obj.target.id, inner_text)
			obj_response.script(extra_script)
			obj_response.script("$('#loading_holder').css('display','none');")

		route_list = request.path[1:].split("/")
		route_name = '_'.join(route_list)
		session[route_name+"current_page"] = FSubmissionSijaxHandler.current_page
		
	@staticmethod
	# @exception_handler
	def _dump_data(obj_response, files, form_values, fsubmission_obj, **kwargs):
		def dump_files():
			if 'file' not in files:
				return {"indicator": True, "message": 'Bad upload'}

			file_data = files['file']
			file_name = file_data.filename
			if file_name is None:
				return {"indicator": True, "message": 'Nothing uploaded'}

			upload_form = fsubmission_obj.origin.find_parent(fsubmission_obj.origin, "upload_form")
			upload_file = upload_form.find_class(upload_form, "uploadFile")

			filename = ""
			for _upload_file in upload_file:
				if file_data and allowed_file(file_data.filename, _upload_file.value["accept_type"]):
					print("file_data.save")
					filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S")+"_"+secure_filename(file_data.filename)
					file_data.save(os.path.join(_upload_file.value["file_path"], filename))
					# print(os.path.join(_upload_file.value["file_path"], filename))

			file_type = file_data.content_type
			file_size = len(file_data.read())
			return {"indicator": True, "message": filename}

		temp_func = fsubmission_obj.func
		response_obj = temp_func(fsubmission_obj, [[dump_files()]])

		# Response according to the return response
		if isinstance(response_obj, list):
			for res_obj in response_obj:
				res_obj.target = res_obj.target if res_obj.target else fsubmission_obj.target
				res_obj.response(obj_response)
		elif response_obj:
			response_obj.target = response_obj.target if response_obj.target else fsubmission_obj.target
			response_obj.response(obj_response)
		else:
			inner_text, extra_script = alert_response({"alert_type":"alert-warning", "alert_message":"系統異常", "alert_position":"prepend"}, fsubmission_obj.origin.id)
			# args[0] is the sijax response object
			obj_response.html_prepend('#'+fsubmission_obj.target.id, inner_text)
			obj_response.script(extra_script)
			obj_response.script("$('#loading_holder').css('display','none');")

	@staticmethod
	# @exception_handler
	def upload_form_handler(obj_response, files, form_values):

		print("========================== upload_form_handler ==========================")
		if isinstance(form_values["fsubmission_obj"], str):
			fsubmission_obj = get_fsubmission_obj(FSubmissionSijaxHandler.current_page, form_values["fsubmission_obj"])
		else:
			fsubmission_obj = get_fsubmission_obj(FSubmissionSijaxHandler.current_page, form_values["fsubmission_obj"][0])
		FSubmissionSijaxHandler._dump_data(obj_response, files, form_values, fsubmission_obj)

		route_list = request.path[1:].split("/")
		route_name = '_'.join(route_list)
		session[route_name+"current_page"] = FSubmissionSijaxHandler.current_page

		# I don't know why flask doesn't get into app.session_interface.save_session in 
		# the end of this request, so I directly call the function so that the value can
		# be saved into redis server
		Famcy.FManager["CurrentApp"].session_interface.save_session(Famcy.FManager["CurrentApp"], session, Response())


class FSubmission:
	"""
	This is the submission object that
	handles all the famcy submission 
	system. 

	- Rep
		* func: user defined function
		* target: the target of the submission block
		* origin: the origin widget of the submission
	"""
	def __init__(self, origin):
		self.func = None
		self.origin = origin
		self.target = origin

	def getFormData(self):
		"""
		This is the getter method
		to get the form layout data. 
		"""
		data = getattr(self.origin.parent, "layout", None)
		assert data, "Submission origin has no data. "
		return data

	def jsAlertHandler(self, submission_obj, info_dict):
		"""
		info_dict = {"alert_type": "", "alert_message": "", "alert_position": ""}
		"""
		print("========================== jsAlertHandler ==========================")
		return Famcy.UpdateAlert(alert_type=info_dict["alert_type"], alert_message=info_dict["alert_message"], alert_position=info_dict["alert_position"])


class FBackgroundTask(FSubmission):
	"""
	This is the background task submission
	object for the background loop.
	"""
	def __init__(self, origin):
		super(FBackgroundTask, self).__init__(origin)
		self.background_info_dict = {}
		self.obj_key = "background"+str(id(self))

	def associate(self, function, info_dict={}, target=None, update_attr={}):
		self.func = function
		self.target = target if target else self
		self.background_info_dict = info_dict
		self.target_attr = update_attr

	def tojson(self, str_format=False):
		self.func(self, self.background_info_dict)

		if isinstance(self.target, list):
			target_html = []
			target_id = []
			for t in self.target:
				if isinstance(t, Famcy.FamcyElement):
					_ = t.render_inner()
					target_html.append(t.html)
					target_id.append(t["id"])
				else:
					_body = t.render()
					_ = _body.render_inner()
					target_html.append(_body.html)
					target_id.append(t.id)
		else:
			if isinstance(self.target, Famcy.FamcyElement):
				_ = self.target.render_inner()
				target_html = self.target.html
				target_id = self.target["id"]
			else:
				_body = self.target.render()
				_ = _body.render_inner()
				target_html = _body.html
				target_id = self.target.id
		
		content = {"data": self.background_info_dict, "submission_id": str(self.obj_key), 
			"page_id": self.origin.id, "target_id": target_id, "target_innerHTML": target_html, "target_attribute": self.target_attr}
		return content if not str_format else json.dumps(content)


