import http.server
from typing import Optional, Any
import urllib.parse


class AuthRequestHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self) -> None:
		# Handle errors here
		...
		self.send_error(404)

	def do_POST(self) -> None:
		# Verify URL
		if self.path != "/authcallback":
			self.send_error(404)
			return

		# Read and parse data
		length = self.headers["Content-Length"]
		data = self.rfile.read(int(length))
		qs = urllib.parse.parse_qs(data.decode())
		authData = {k: v[0] for k, v in qs.items()}

		# Verify state
		if "state" not in authData or authData["state"] != self.server._state:
			self.send_error(403, "Wrong state", "The state argument is invalid or incorrect")
			return

		# Ensure everything is present
		if "access_token" not in authData or "expires_in" not in authData:
			self.send_error(
				400,
				"Missing token",
				"Authentication token was not present in the request",
			)
			return
		self.server.received_auth_data(authData)

		# Send a simple response back to the user
		self.send_response(200)
		self.end_headers()
		self.wfile.write("""
			<html>
				<head>
					<script type="text/javascript">window.close();</script>
				</head>
				<body>
					Authentication successful. You may now close this page.
				</body>
			</html>
		""".encode())

	def log_message(self, *args, **kwargs):
		# Disable logging
		pass


class AuthHTTPServer(http.server.HTTPServer):
	def __init__(self, port: int, state: str) -> None:
		super().__init__(("localhost", port), AuthRequestHandler)
		self._authData: Optional[dict[str, Any]] = None
		self._state = state

	def received_auth_data(self, data: dict[str, Any]) -> None:
		self._authData = data

	def await_auth_data(self) -> dict[str, Any]:
		while self._authData is None:
			self.handle_request()
		self.server_close()
		return self._authData
