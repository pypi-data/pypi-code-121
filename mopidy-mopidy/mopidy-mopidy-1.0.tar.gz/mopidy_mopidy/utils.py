

class Utils:
  @staticmethod
  def uri_to_master(uri):
        params = uri.split(':')
        params.pop(0)
        params.pop(0)
        uri = ":".join(params)
        return uri
