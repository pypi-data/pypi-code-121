from jinja2 import Template
from kedro_fast_api.models.config import Config
from kedro_fast_api.utils import project_path
class ApiFactory:
    def __init__(self, path) -> None:
        self.config = Config(path)

    def create_app_file(self) -> None:
        path = project_path("templates/api_template.j2")
        template = Template(path.open().read())
        rendered = template.render(
            routes=self.config.routes,
            security=self.config.security,
            title=self.config.title,
            description=self.config.description,
            version=self.config.version,
            tags=self.config.tags
        )
        with open('app.py', 'w') as file:
            file.write(rendered)
