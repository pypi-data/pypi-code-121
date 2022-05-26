import Famcy

class UpdateCallback(Famcy.FamcyResponse):
	def __init__(self, target=None, callback=None):
		super(UpdateCallback, self).__init__(target=target)
		self.callback = callback

	def response(self, sijax_response):
		if self.callback:
			self.callback()
		sijax_response.script(self.finish_loading_script)