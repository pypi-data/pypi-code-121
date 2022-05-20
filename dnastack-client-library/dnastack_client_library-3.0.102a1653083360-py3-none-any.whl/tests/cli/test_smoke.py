from tests.cli.base import CliTestCase


class TestConfiguration(CliTestCase):
    def test_happy_path(self):
        # No assertion here as long as nothing throws an error.
        # dnastack config set collections.url https://viral.ai/api/
        self.invoke('config', 'set', 'collections.url', 'https://viral.ai/api/', bypass_error=False)
        # dnastack collections list
        self.invoke('collections', 'list', bypass_error=False)
        # dnastack collections tables list ncbi-sra
        self.invoke('collections', 'tables', 'list', '--collection', 'ncbi-sra', bypass_error=False)
        # dnastack collections query ncbi-sra "SELECT 1"
        self.invoke('collections', 'query', '--collection', 'ncbi-sra', 'SELECT 1', bypass_error=False)
