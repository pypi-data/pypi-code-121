class Product:
    def __init__(self, source):
        self.description = source["description"]
        self.name = source["name"]
        self.has_full_access = source["has_full_access"]
        self.has_quota = source["has_quota"]
        self.quota = source["has_quota"] if self.has_quota else None
        self.tier_id = source["tier_id"]
        self.price = source["price"]
        self.has_trial = source["has_trial"]
        self.trial_length = source["trial_length"] if self.has_trial else None
        self.trial_time_frame = source["trial_time_frame"] if self.has_trial else None
        self.is_free = source["is_free"]
