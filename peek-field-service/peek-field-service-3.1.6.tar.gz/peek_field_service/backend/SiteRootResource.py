import os

from txhttputil.site.SiteUtil import RedirectionRule

from peek_platform import PeekPlatformConfig
from txhttputil.site.FileUnderlayResource import FileUnderlayResource
from vortex.VortexFactory import VortexFactory

docSitePrefix = "/docs/"
fieldRoot = FileUnderlayResource()
for r in [
    RedirectionRule("/docs", docSitePrefix),
    RedirectionRule("/doc", docSitePrefix),
    RedirectionRule("/help", docSitePrefix),
    RedirectionRule("/documentation", docSitePrefix),
]:
    fieldRoot.addRedirectionRule(r)


def setupField():
    # Setup properties for serving the site
    fieldRoot.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent

    import peek_field_app

    frontendProjectDir = os.path.dirname(peek_field_app.__file__)
    distDir = os.path.join(frontendProjectDir, "dist")

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    fieldRoot.addFileSystemRoot(distDir)

    addVortexServers(fieldRoot)
    addDocSite(fieldRoot)


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

    import peek_field_doc

    docProjectDir = os.path.dirname(peek_field_doc.__file__)
    distDir = os.path.join(docProjectDir, "doc_dist")

    distDirParent = os.path.dirname(distDir)
    if not os.path.isdir(distDirParent):
        raise NotADirectoryError(distDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    docSiteRoot.addFileSystemRoot(distDir)

    siteRootResource.putChild(b"docs", docSiteRoot)
