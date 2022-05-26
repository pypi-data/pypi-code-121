import Famcy

class UpdateBlockHtml(Famcy.FamcyResponse):
	"""
	This is the response to update a specific
	part of the famcy widget
	"""
	def __init__(self, extra_script=None, target=None, upload_flag=False):
		super(UpdateBlockHtml, self).__init__(target=target)
		self.extra_script = extra_script
		self.upload_flag = upload_flag

	def response(self, sijax_response):
		if self.target:
			# update body html
			_id = self.target["id"] if isinstance(self.target, Famcy.FamcyElement) else self.target.id
			_body = self.target if isinstance(self.target, Famcy.FamcyElement) else self.target.render()
			_ = _body.render_inner()
			pure_html = self.run_all_script_tag(_body.html, sijax_response) if self.upload_flag else _body.html
			sijax_response.html('#'+_id, pure_html)

			if hasattr(self.target, "layout"):
				self.target.layout.setSijaxLayout(sijax_response)
			sijax_response.script(self.extra_script)
			sijax_response.script(self.finish_loading_script)