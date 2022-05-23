from typing import Optional, Tuple, Any, Dict, Type

from wai.test import AbstractTest
from wai.test.decorators import Test, ExceptionTest

from wai.common import TwoWayDict


class TwoWayDictTest(AbstractTest):
    @classmethod
    def subject_type(cls):
        return TwoWayDict[int, str]

    @Test
    def insert_and_retrieve(self, subject: TwoWayDict[int, str]):
        subject[2] = "asd"
        self.assertEqual(subject["asd"], 2)

    @ExceptionTest(TypeError)
    def insert_wrong_type(self, subject: TwoWayDict[int, str]):
        subject[3] = 3.4

    @Test
    def insert_class(self, subject: TwoWayDict[int, str]):
        class Base:
            pass

        class B1(Base):
            pass

        class B2(Base):
            pass

        new_subject = TwoWayDict[str, Type[Base]]()

        new_subject["B1"] = B1
        new_subject[B2] = "B2"

        self.assertIn(B1, new_subject)
        self.assertIn(B2, new_subject)
        self.assertIn("B1", new_subject)
        self.assertIn("B2", new_subject)
        self.assertEqual(new_subject[B1], "B1")
        self.assertEqual(new_subject["B2"], B2)
