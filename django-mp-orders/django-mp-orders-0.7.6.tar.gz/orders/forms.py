
from django import forms

from orders.models import Order

from delivery.fields import DeliveryFormField


class CheckoutForm(forms.ModelForm):

    delivery = DeliveryFormField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['delivery'].init_form(*args, **kwargs)

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'middle_name', 'payment_method',
            'mobile', 'comment'
        ]
