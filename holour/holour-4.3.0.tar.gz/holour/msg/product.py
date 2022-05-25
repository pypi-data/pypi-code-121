from holour.msg import Pose


class Product:

    def __init__(self, uuid: str, name: str, image: str, category: str, process_uuid: str = "", pick_pose: Pose = None,
                 agents: [str] = None, tags: [str] = None, description: str = "", _type: str = ''):
        assert type(uuid) == str
        assert type(name) == str
        assert type(image) == str
        assert type(category) == str
        assert type(process_uuid) == str
        if pick_pose:
            assert type(pick_pose) == Pose
        assert type(agents) == list or agents is None
        assert type(tags) == list or tags is None
        assert type(description) == str

        self._type = 'product'
        self.uuid = uuid
        self.name = name
        self.image = image
        self.category = category
        self.process_uuid = process_uuid
        self.pick_pose = pick_pose
        self.agents = agents if agents else []
        self.tags = tags if tags else []
        self.description = description

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Product):
            return other.uuid == self.uuid \
                   and other.name == self.name \
                   and other.image == self.image \
                   and other.category == self.category \
                   and other.process_uuid == self.process_uuid \
                   and other.pick_pose == self.pick_pose \
                   and other.agents == self.agents \
                   and other.tags == self.tags \
                   and other.description == self.description
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<id={self.uuid},name={self.name},image={self.image},category={self.category}" \
               f",process_uuid={self.process_uuid},pick_pose={self.pick_pose},agents={self.agents}," \
               f"tags={self.tags},description={self.description}>"
