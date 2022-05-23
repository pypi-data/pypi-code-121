import os

# Turns on debugging features in Flask
DEBUG = True

# secret key:
SECRET_KEY = "MySuperSecretKey"

# Database connection parameters
DB_HOST = os.getenv("MONGODB_HOST") or "127.0.0.1"
DB_PORT = 27017
DB_NAME = "cgbeacon2-test"
DB_URI = f"mongodb://{DB_HOST}:{DB_PORT}/{DB_NAME}"  # standalone MongoDB instance
# DB_URI = "mongodb://localhost:27011,localhost:27012,localhost:27013/?replicaSet=rs0" # MongoDB replica set

# ADMINS will receive email notification is app crashes
# MAIL_SERVER = "smtp.gmail.com"
# MAIL_PORT = 587
# MAIL_USE_TLS = True
# MAIL_USE_SSL = False
# MAIL_USERNAME = "system.email@email.com"
# MAIL_PASSWORD = "password"
# ADMINS = ["admin.email@email.com"]

ORGANIZATION = dict(
    id="scilifelab",  # mandatory
    name="Clinical Genomics, SciLifeLab",  # mandatory
    description="Science for Life Laboratory",
    address="Tomtebodavägen 23, 17165 Solna, Sweden",
    contactUrl="mailto:admin@scilifelab.beacon.com",
    logoUrl="https://raw.githubusercontent.com/Clinical-Genomics/cgbeacon2/8370809507e08a4fa6724bbf0bc6e9b581d1fa76/cgbeacon2/server/static/scilifelab-logo.svg",
)

BEACON_OBJ = dict(
    id="SciLifeLab-beacon",  # mandatory
    name="SciLifeLab Stockholm Beacon",  # mandatory
    organization=ORGANIZATION,  # mandatory
    createDateTime="2015-06-15T00:00.000Z",
    description="Beacon description",
    welcomeUrl="https://beacon-stage.scilifelab.se/apiv1.0/query_form",
    alternativeUrl="https://beacon-stage.scilifelab.se/apiv1.0/",
)

############## OAUTH2 permissions layer ##############
### https://elixir-europe.org/services/compute/aai ###
ELIXIR_OAUTH2 = dict(
    server="https://login.elixir-czech.org/oidc/jwk",  # OAuth2 server that returns JWK public key
    issuers=["https://login.elixir-czech.org/oidc/"],  # Authenticated Bearer token issuers
    userinfo="https://login.elixir-czech.org/oidc/userinfo",  # Where to send access token to view user data (permissions, statuses, ...)
    audience=[],  # List of strings. Service(s) the token is intended for. (key provided by the Beacon Network administrator)
    verify_aud=False,  # if True, force verify audience for provided token
    bona_fide_requirements="https://doi.org/10.1038/s41431-018-0219-y",
)
