from test.base import ClientBaseCase

from lendsmart_api.objects import Document


class DocumentTest(ClientBaseCase):
    """
    Tests methods of the Document class
    """
    def test_get_document(self):
        """
        Tests that an document is loaded correctly by ID
        """
        doc = Document(self.client, 'linode/debian9')
        self.assertEqual(doc._populated, False)

        self.assertEqual(doc.label, 'Debian 9')
        self.assertEqual(doc._populated, True)
