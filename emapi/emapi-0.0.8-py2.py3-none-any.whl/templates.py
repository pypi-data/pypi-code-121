from tempy import Escaped
from tempy.widgets import TempyPage
from tempy.tags import Link, Div, Script


class Swagger(TempyPage):
	def __init__(self, *args, title="", openapi_url="", **kwargs):
		self.title = title
		self.openapi_url = openapi_url
		super().__init__(*args, **kwargs)

	def init(self):
		self.head(
			Link(href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css", rel="stylesheet", typ="text/css"),
			Link(href="https://fastapi.tiangolo.com/img/favicon.png", rel="shortcut icon",),
		)
		self.head.title(self.title)
		self.body(
			Div(id="swagger-ui"),
			Script(src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"),
			Script()(
				Escaped(
					f"""
const ui = SwaggerUIBundle({{ url: '{self.openapi_url}', dom_id: '#swagger-ui', presets: [SwaggerUIBundle.presets.apis,SwaggerUIBundle.SwaggerUIStandalonePreset],layout: "BaseLayout", deepLinking: true, showExtensions: true, showCommonExtensions: true }})"""
				)
			),
		)
