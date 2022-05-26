class PartnerEmailChangeService:
    def __init__(self, env):
        self.env = env

    def run_from_api(self, **params):
        self.env['partner.email.change.wizard'].with_delay().run_from_api_partner(
            **params
        )
        return {"result": "OK"}
