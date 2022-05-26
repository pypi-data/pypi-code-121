from servicefoundry.internal.template.generated_definition import GeneratedDefinition


class PackagedComponent:
    def __init__(self, build_dir, service_def):
        self.build_dir = build_dir
        self.service_def: GeneratedDefinition = service_def
