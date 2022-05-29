
class Tags():

    tags = {}

    @classmethod
    def register(cls, tag_class):
        tag = tag_class.yaml_tag
        cls.tags[tag] = tag_class
        return tag_class

    @classmethod
    def save_tags(cls, yaml):
        for tag, tag_class in cls.tags.items():
            yaml.SafeLoader.add_constructor(tag, tag_class.from_yaml)
            yaml.SafeDumper.add_multi_representer(tag_class, tag_class.to_yaml)