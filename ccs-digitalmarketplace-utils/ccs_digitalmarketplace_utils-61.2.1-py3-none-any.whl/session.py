
import flask_session
import redis

import dmutils.cloudfoundry as cf


def init_app(app):
    if not app.config.get("SESSION_REDIS"):
        if app.config.get("DM_ENVIRONMENT") == "development":
            app.config["SESSION_REDIS"] = redis.Redis()
        else:
            vcap_services = cf.get_vcap_services()

            redis_service_name = app.config["DM_REDIS_SERVICE_NAME"]
            redis_service = cf.get_service_by_name_from_vcap_services(vcap_services, redis_service_name)

            app.config["SESSION_REDIS"] = redis.from_url(redis_service["credentials"]["uri"])

    # patch for aws clone
    else:
        redis_uri = app.config.get("SESSION_REDIS")
        redis_host = redis_uri.split(':')[0]
        redis_port = int(redis_uri.split(':')[1])
        app.config["SESSION_REDIS"] = redis.Redis(host=redis_host, port=redis_port)

    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_TYPE"] = 'redis'
    flask_session.Session(app)
