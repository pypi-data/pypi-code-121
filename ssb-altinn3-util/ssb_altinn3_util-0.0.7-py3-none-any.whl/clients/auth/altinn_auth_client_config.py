class AltinnAuthClientConfig:
    """
    Configuration class for AltinnAuthClient
    """

    def __init__(
        self,
        maskinport_client_id: str,
        keycloak_secret_path: str,
        platform_environment: str,
        altinn_base_url: str,
    ):
        """
        :param maskinport_client_id: A valid client id in Maskinporten
        :param keycloak_secret_path: The path to the keycloak secret (in GCP secret manager)
        :param platform_environment: Runtime environment for ssb subsystems (staging or prod)
        :param altinn_base_url: Base url for the Altinn Authentication API
        """
        self.maskinport_client_id = maskinport_client_id
        self.keycloak_secret_path = keycloak_secret_path
        self.platform_environment = platform_environment
        self.altinn_base_url = altinn_base_url
