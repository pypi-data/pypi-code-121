from datetime import datetime, timedelta


class ArchiveDateManagement:

    def __init__(self, collection, archive_date):
        self.archive_date = archive_date
        caller = getattr(self, collection, None)
        if caller:
            caller(archive_date)

    def woao(self, archive_date):
        # This is the Monday of the next week
        r = datetime.strptime(archive_date, "%Y-%B-%d")
        self.archive_date = r.strftime('%Y-%m-%d')

    def frtm(self, archive_date):
        # This is the Monday of the next week
        archive_date = archive_date + '-1'
        r = datetime.strptime(archive_date, "%Y-%W-%w")
        # Go back 3 days
        friday = r - timedelta(days=3)
        self.archive_date = friday.strftime('%Y-%m-%d')


    def detm(self, archive_date):
        # This is the Monday of the next week
        archive_date = archive_date + '-1'
        r = datetime.strptime(archive_date, "%Y%W-%w")
        # Go back 3 days
        friday = r - timedelta(days=3)
        self.archive_date = friday.strftime('%Y-%m-%d')

