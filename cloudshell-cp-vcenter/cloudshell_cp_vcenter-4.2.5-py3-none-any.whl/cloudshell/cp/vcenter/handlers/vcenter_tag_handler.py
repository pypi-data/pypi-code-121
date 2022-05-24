from cloudshell.cp.core.utils.tags import BaseTagsManager


class VCenterTagsManager(BaseTagsManager):
    @classmethod
    def get_tags_created_by(cls):
        return {cls.DefaultTagNames.created_by: cls.DefaultTagValues.created_by}
