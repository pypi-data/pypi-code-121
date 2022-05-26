import dataclasses


@dataclasses.dataclass(frozen=True)
class ArtifactCredential:
    run_id: str
    path: str
    signed_uri: str
