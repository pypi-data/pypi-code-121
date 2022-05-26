from mako.template import Template

from servicefoundry.internal.predictor import Predictor


def main_file_interceptor(predictor: Predictor):
    def _main_file_interceptor(source):
        template = Template(source)
        return template.render(
            functions=predictor.interceptor.get_functions(),
            module_name=predictor.interceptor.module_name,
        )

    return _main_file_interceptor
