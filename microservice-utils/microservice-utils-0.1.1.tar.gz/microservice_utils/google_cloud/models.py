import google.auth


class GcpProjectConfig:
    __slots__ = ("id", "region", "service_account_email")

    def __init__(self, region: str):
        credentials, project_id = google.auth.default()

        self.id = project_id
        self.region = region
        self.service_account_email = (
            credentials.service_account_email
            if hasattr(credentials, "service_account_email")
            else None
        )

    @property
    def location_path(self):
        return f"projects/{self.id}/locations/{self.region}"
