
from django.test import TestCase

from product_barcode.models import BarCode


class BarCodeTestCase(TestCase):

    def setUp(self):
        self._barCode = BarCode.objects.create(next_code=10)

    def test_codes_generation(self):

        self.assertEqual(
            BarCode.objects.get().get_next_codes(3),
            ['0000000000109', '0000000000116', '0000000000123']
        )

        self._barCode.next_code = 100
        self._barCode.save()

        self.assertEqual(
            BarCode.objects.get().get_next_codes(3),
            ['0000000001007', '0000000001014', '0000000001021']
        )

        self._barCode.next_code = 1234
        self._barCode.save()

        self.assertEqual(
            BarCode.objects.get().get_next_codes(3),
            ['0000000012348', '0000000012355', '0000000012362']
        )
