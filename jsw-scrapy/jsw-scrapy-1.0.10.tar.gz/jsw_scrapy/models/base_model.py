from orator import Model
import pendulum


class BaseModel(Model):
    __guarded__ = []

    @classmethod
    def find_or_new_by(cls, options):
        entity = cls.find_by(options)
        if not entity:
            entity = cls()
            for k in options:
                v = options[k]
                setattr(entity, k, v)
        return entity

    @classmethod
    def find_by(cls, options):
        return cls.where(options).first()

    # normalize timezone
    def fresh_timestamp(self):
        return pendulum.now('Asia/Shanghai')
