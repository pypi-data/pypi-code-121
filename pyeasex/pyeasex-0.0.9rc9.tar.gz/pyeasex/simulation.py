class Task():
  def __init__(self, project_uuid, api, input):
    self.project_uuid = project_uuid
    self.api = api
    self.input = input

  def prepare(self):
    pass

  def run(self):
    pass

  def complete(self):
    pass

  def terminate(self, exception_code):
    pass