from src.pylimiter.backend.default import DefaultBackend


class Client:
    def __init__(self, project_id, opts):
        self.project_id = project_id

        if opts['backend'] == 'Default':
            self.backend = DefaultBackend(self.project_id, opts)

    def bind(self, plan_id, user_id):
        return self.backend.bind(plan_id, user_id)

    def feature(self, feature_id, user_id):
        return self.backend.feature(feature_id, user_id)

    def increment(self, feature_id, user_id):
        return self.backend.increment(feature_id, user_id)

    def decrement(self, feature_id, user_id):
        return self.backend.decrement(feature_id, user_id)

    def set(self, feature_id, user_id, value):
        return self.backend.set(feature_id, user_id, value)

    def feature_matrix(self):
        return self.backend.feature_matrix()

    def usage(self, user_id):
        return self.backend.usage(user_id)
