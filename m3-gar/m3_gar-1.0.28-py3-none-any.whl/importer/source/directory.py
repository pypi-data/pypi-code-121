from m3_gar.importer.source.tablelist import (
    TableList,
)
from m3_gar.importer.source.wrapper import (
    DirectoryWrapper,
)


class DirectoryTableList(TableList):
    wrapper_class = DirectoryWrapper

    def load_data(self, source):
        return self.wrapper_class(source=source, is_temporary=False)
