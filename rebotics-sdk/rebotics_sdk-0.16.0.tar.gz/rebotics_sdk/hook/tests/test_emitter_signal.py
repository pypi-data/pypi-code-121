from unittest.mock import MagicMock, patch

from django.dispatch import receiver
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from rebotics_sdk.hook.signals import PROCESSING_FINISH_SUCCESS
from rebotics_sdk.hook.views import WebhookHandlerViewSet


class SignalEmitterTestCase(APITestCase):
    def test_success(self):
        mock = MagicMock()
        mock.return_value = None
        receiver(PROCESSING_FINISH_SUCCESS)(mock)

        factory = APIRequestFactory()
        request = factory.post(
            "/webhook/testretailer/",
            data={
                "event": "processing.finish",
                "payload": {
                    "id": 123,
                    "status": "done",
                }
            },
            format='json'
        )
        with patch("rebotics_sdk.hook.signals.SignalEmitter.send_signal") as signal_mock:
            view = WebhookHandlerViewSet.as_view()
            response = view(request, retailer_code="testretailer")
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            signal_mock.assert_called_once()

    def test_success_called_with_check(self):
        mock = MagicMock()
        mock.return_value = None
        receiver(PROCESSING_FINISH_SUCCESS)(mock)

        factory = APIRequestFactory()
        request = factory.post(
            "/webhook/testretailer/",
            data={
                "event": "processing.finish",
                "payload": {
                    "id": 123,
                    "status": "done",
                }
            },
            format='json'
        )
        with patch("rebotics_sdk.hook.signals.SignalEmitter") as signal_mock_2:
            view = WebhookHandlerViewSet.as_view()
            response = view(request, retailer_code="testretailer")
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            signal_mock_2.assert_called_with(
                retailer="testretailer",
                event="processing.finish",
                payload={
                    "id": 123,
                    "status": "done",
                }
            )

    def test_no_fields(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/webhook/testretailer/",
            data={},
            format='json'
        )

        view = WebhookHandlerViewSet.as_view()
        response = view(request, retailer_code="testretailer")
        error_data = {
            "event": ["This field is required."],
            "payload": ["This field is required."]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, error_data)

    def test_different_event(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/webhook/testretailer/",
            data={
                "event": "hello",
                "payload": {
                    "id": 123,
                    "status": "done",
                }
            },
            format='json'
        )

        view = WebhookHandlerViewSet.as_view()
        response = view(request, retailer_code="testretailer")
        error_data = {
            "event": ["\"hello\" is not a valid choice."]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, error_data)

    def test_no_status(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/webhook/testretailer/",
            data={
                "event": "processing.finish",
                "payload": {
                    "id": 123
                }
            },
            format='json'
        )

        view = WebhookHandlerViewSet.as_view()
        response = view(request, retailer_code="testretailer")
        error_data = {
            "payload":
                {
                    "status": ["This field is required."]
                }
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, error_data)
