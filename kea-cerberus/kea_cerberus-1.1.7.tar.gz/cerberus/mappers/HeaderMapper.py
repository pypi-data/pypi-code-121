

from cerberus.responses.HeaderRS import HeaderRS

class HeaderMapper():

    def mapToHeader(session):
        header = HeaderRS(session.getToken(),session.getCreatedAt(),session.getUpdatedAt());
        return header;
