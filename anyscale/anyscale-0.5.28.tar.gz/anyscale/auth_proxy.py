from typing import Optional

from aiohttp import web
from aiohttp_middlewares import cors_middleware  # type: ignore

from anyscale import ANYSCALE_ENV


async def error_page(request: web.Request) -> web.Response:
    # Serve custom error page for the services
    return web.Response(
        text="""
<html>
    <head>
        <title> Retrying </title>
        <meta http-equiv="refresh" content="5">
        <style>
        body {
            font-family: noto sans,sans-serif;
            padding: 25px;
        }
        </style>
    </head>
    <body>
      <h1>
        Loading...
      </h1>

      <h2> ⌛ </h2>
      <p> Service currently unavailable. </p>
      <p> This page will automatically refresh. </p>

    </body>
</html>
        """,
        status=502,  # bad gateway
        content_type="text/html",
    )


async def index(request: web.Request) -> web.Response:
    token = request.query.get("token")
    redirect_to = request.query.get("redirect_to")
    # Sometimes we don't want to perform the redirect.
    # We just want to authenticate and download the cookie,
    # for example in the case of the WebTerminal.
    auth_only = request.query.get("auth_only")

    host = request.headers.get("Host")
    if "serve" in host:
        redirect_to = "https://" + host
        if request.query.get("redirect_to"):
            redirect_to += "/" + request.query.get("redirect_to")

    path = {
        "tensorboard": "/tensorboard/",
        "grafana": "/grafana/",
        "dashboard": "/",
        "hosted_dashboard": "/metrics/redirect",
        "webterminal": "/webterminal/",
        "anyscaled": "/anyscaled/",
        "metrics": "/metrics",
        "autoscalermetrics": "/autoscalermetrics",
        "serve": "/serve",
    }

    if (
        not token
        or not redirect_to
        # If host contains "serve-": redirect_to will equal the host, instead of a key in `path`
        or ("serve" not in host and redirect_to not in path)
    ):
        return web.Response(
            text="token or redirect_to field not found, "
            "maybe you forgot to add `?token=..&redirect_to.` field? "
            "redirect_to={tensorboard, dashboard, grafana, webterminal, serve}.",
            status=401,
        )

    if auth_only is None and "serve" in host:
        resp = web.HTTPFound(redirect_to)
    elif auth_only is None:
        resp = web.HTTPFound(path[redirect_to])
    else:
        resp = web.Response(text="ok")

    use_secure = (
        ANYSCALE_ENV.get("ANYSCALE_HOST") == "https://beta.anyscale.com"
        or ANYSCALE_ENV.get("ANYSCALE_HOST") == "https://console.anyscale.com"
    ) and redirect_to != "dashboard"
    if redirect_to == "webterminal":
        # The default for samesite is None currently but it is migrating
        # to Lax for most browser. Explicitly setting it here will
        # enable console.anyscale.com to communicate with webterminal service.
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
        resp.set_cookie("anyscale-token", token, secure=True, samesite="None")
    else:
        resp.set_cookie("anyscale-token", token, secure=use_secure)
    return resp


async def authorize_user_service(request: web.Request) -> web.Response:
    unauthorized_message = (
        "If viewing in a web browser, please first visit the FastAPI documentation link. "
        "You can find the FastAPI link by navigating to the cluster page and clicking on "
        "the Deployments tab. Otherwise, please include the cluster's user_service_token "
        "in the Authorization bearer headers of the request. The user_service_token can "
        "be found on the cluster page under Network Access."
    )
    if not request.config_dict["user_service_token"]:
        return web.Response(text=unauthorized_message, status=401)

    auth_token = request.config_dict["user_service_token"]
    cookies = request.cookies
    if cookies.get("anyscale-token") == auth_token:
        return web.Response(text="Authorized", status=200)
    headers = request.headers
    if (
        headers.get("Authorization") == f"Bearer {auth_token}"
        or headers.get("Authorization") == f"bearer {auth_token}"
    ):
        return web.Response(text="Authorized", status=200)

    return web.Response(text=unauthorized_message, status=401)


async def authorize(request: web.Request) -> web.Response:
    print(
        "Got authorization request for:",
        request.headers.get("X-Forwarded-Uri", "unknown"),
    )

    use_token = request.query.get("use_token", "access_token")
    if use_token == "access_token":
        auth_token = request.config_dict["auth_token"]

        cookies = request.cookies
        if cookies.get("anyscale-token") == auth_token:
            return web.Response(text="Authorized", status=200)
        headers = request.headers
        if (
            headers.get("Authorization") == f"Bearer {auth_token}"
            or headers.get("Authorization") == f"bearer {auth_token}"
        ):
            return web.Response(text="Authorized", status=200)

        unauthorized_message = (
            "Unauthorized. Please navigate to this resource through the cluster's page in the Anyscale "
            "product. Doing so will automatically authorize this request from a web browser. Please "
            "include the `anyscale-token` in the cookies if not performing this request from a web "
            "browser."
        )
        return web.Response(text=unauthorized_message, status=401)
    else:
        return await authorize_user_service(request)


def make_auth_proxy_app(
    auth_token: str, user_service_token: Optional[str]
) -> web.Application:
    auth_app = web.Application()
    auth_app.add_routes(
        [
            web.get("/", index),
            web.get("/authorize", authorize),
            web.get("/error_page", error_page),
        ]
    )

    origins = []
    # ANYSCALE_ENV is only a dictionary values when
    # this server runs on the head node.
    # If its a dictionary, use the ANYSCALE_HOST as whitelisted host
    # these values could be an IP address in developer instances
    # or console.anyscale.com in production
    if "ANYSCALE_HOST" in ANYSCALE_ENV:
        origins = [ANYSCALE_ENV["ANYSCALE_HOST"]]

    app = web.Application(
        middlewares=[cors_middleware(origins=origins, allow_credentials=True)]
    )

    app.add_subapp("/auth", auth_app)
    app["auth_token"] = auth_token
    app["user_service_token"] = user_service_token

    return app
