class MCDDNSError(Exception):
    pass


class NoSuchProviderType(MCDDNSError):
    pass


class NoSuchProvider(MCDDNSError):
    pass
