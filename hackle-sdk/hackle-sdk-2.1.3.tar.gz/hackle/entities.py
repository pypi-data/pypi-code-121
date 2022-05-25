import abc

ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class BaseEntity(object):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class BaseExperiment(ABC, BaseEntity):
    def __init__(self, id, key, type, variations, user_overrides):
        self.id = id
        self.key = key
        self.key = key
        self.type = type
        self.variations = variations
        self.user_overrides = user_overrides

    def get_variation_by_id_or_none(self, variation_id):
        for variation in self.variations:
            if variation.id == variation_id:
                return variation

        return None

    def get_variation_by_key_or_none(self, variation_key):
        for variation in self.variations:
            if variation.key == variation_key:
                return variation

        return None

    def get_overridden_variation_or_none(self, user):
        overridden_variation_id = self.user_overrides.get(user.id)
        if not overridden_variation_id:
            return None
        return self.get_variation_by_id_or_none(overridden_variation_id)


class DraftExperiment(BaseExperiment):
    def __init__(self, id, key, type, variations, user_overrides):
        super(DraftExperiment, self).__init__(id, key, type, variations, user_overrides)


class RunningExperiment(BaseExperiment):
    def __init__(self, id, key, type, variations, user_overrides, target_audiences, target_rules, default_rule):
        super(RunningExperiment, self).__init__(id, key, type, variations, user_overrides)
        self.target_audiences = target_audiences
        self.target_rules = target_rules
        self.default_rule = default_rule


class PausedExperiment(BaseExperiment):
    def __init__(self, id, key, type, variations, user_overrides):
        super(PausedExperiment, self).__init__(id, key, type, variations, user_overrides)


class CompletedExperiment(BaseExperiment):
    def __init__(self, id, key, type, variations, user_overrides, winner_variation_id):
        super(CompletedExperiment, self).__init__(id, key, type, variations, user_overrides)
        self.winner_variation = self.get_variation_by_id_or_none(winner_variation_id)


class Variation(BaseEntity):
    def __init__(self, id, key, is_dropped):
        self.id = id
        self.key = key
        self.is_dropped = is_dropped


class Bucket(BaseEntity):
    def __init__(self, seed, slot_size, slots):
        self.seed = seed
        self.slot_size = slot_size
        self.slots = slots

    def get_slot_or_none(self, slot_number):
        for slot in self.slots:
            if slot.contains(slot_number):
                return slot
        return None


class Slot(BaseEntity):
    def __init__(self, start_inclusive, end_exclusive, variation_id):
        self.start_inclusive = start_inclusive
        self.end_exclusive = end_exclusive
        self.variation_id = variation_id

    def contains(self, slot_number):
        return (self.start_inclusive <= slot_number) and (slot_number < self.end_exclusive)


class EventType(BaseEntity):
    def __init__(self, id, key):
        self.id = id
        self.key = key


class Target(BaseEntity):
    def __init__(self, conditions):
        self.conditions = conditions


class TargetCondition(BaseEntity):
    def __init__(self, key, match):
        self.key = key
        self.match = match


class TargetKey(BaseEntity):
    def __init__(self, type, name):
        self.type = type
        self.name = name


class TargetMatch(BaseEntity):
    def __init__(self, type, operator, value_type, values):
        self.type = type
        self.operator = operator
        self.value_type = value_type
        self.values = values


class TargetAction(BaseEntity):
    def __init__(self, type, variation_id=None, bucket_id=None):
        self.type = type
        self.variation_id = variation_id
        self.bucket_id = bucket_id


class TargetRule(BaseEntity):
    def __init__(self, target, action):
        self.target = target
        self.action = action
