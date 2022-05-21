class User:
    def __init__(self, source):
        self.apikeys = source["apikeys"]
        self.in_trial = source["is_trial"]
        self.first_seen = source["first_seen"]

        self.status = source["status"]
        self.uid = source["custom_uid"]
        self.tier_id = source["tier_id"]
        self.email = source["email"]

        self.status = source["status"]

        self.attrs = source["attrs"]
        self.in_trial = source["is_trial"]
        if self.in_trial:
            self.trial_end = source["trial_end"]
        ##Quota stuff
        self.has_quota = source["has_quota"]
        if self.has_quota:
            self.max_quota = source["max_quota"]
            self.remaining_quota = source["quota"]
        else:
            self.max_quota = None
            self.remaining_quota = None

    def to_dict(self):
        obj_dict = self.__dict__.copy()
        return obj_dict
