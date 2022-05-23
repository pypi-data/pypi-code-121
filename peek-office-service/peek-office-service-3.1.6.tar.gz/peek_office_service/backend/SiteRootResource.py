import os

from twisted.web.util import Redirect

from peek_platform import PeekPlatformConfig
from txhttputil.site.FileUnderlayResource import FileUnderlayResource
from txhttputil.site.SiteUtil import RedirectionRule
from vortex.VortexFactory import VortexFactory

docSitePrefix = "/docs/"
officeRoot = FileUnderlayResource()
for r in [
    RedirectionRule("/docs", docSitePrefix),
    RedirectionRule("/doc", docSitePrefix),
    RedirectionRule("/help", docSitePrefix),
    RedirectionRule("/documentation", docSitePrefix),
]:
    officeRoot.addRedirectionRule(r)


def setupOffice():
    # Setup properties for serving the site
    officeRoot.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent

    import peek_office_app

    frontendProjectDir = os.path.dirname(peek_office_app.__file__)
    distDir = os.path.join(frontendProjectDir, "dist")

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    officeRoot.addFileSystemRoot(distDir)

    addVortexServers(officeRoot)
    addDocSite(officeRoot)


def addVortexServers(siteRootResource):
    # Add the websocket to the site root
    VortexFactory.createHttpWebsocketServer(
        PeekPlatformConfig.componentName, siteRootResource
    )

    # Add a HTTP vortex
    # VortexFactory.createServer(PeekPlatformConfig.componentName, siteRootResource)


def addDocSite(siteRootResource):
    # Setup properties for serving the site
    docSiteRoot = FileUnderlayResource()
    docSiteRoot.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent

    import peek_office_doc

    docProjectDir = os.path.dirname(peek_office_doc.__file__)
    distDir = os.path.join(docProjectDir, "doc_dist")

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    docSiteRoot.addFileSystemRoot(distDir)

    siteRootResource.putChild(b"docs", docSiteRoot)
