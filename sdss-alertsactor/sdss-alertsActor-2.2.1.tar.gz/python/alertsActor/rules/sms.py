#!/usr/bin/env python
# encoding: utf-8
#
# sms.py
#
# Created by John Donor on 1 Mar 2019.

from twilio.rest import Client
def sendSms(keyState, phoneNumbers=["+18177733196"]):
    # $TWILIO_ACCOUNT_SID and $TWILIO_AUTH_TOKEN must be set
    client = Client()

    severity = keyState.severity
    
    alertTxt = "{} alert on {}".format(severity, keyState.actorKey)

    for n in phoneNumbers:
        print("sms to {}".format(n))
        message = client.messages \
                        .create(
                            body=alertTxt,
                            from_='+19726456866',
                            to=n
                        )
        
        result = client.messages.get(message.sid).fetch()
        print("sms to {} was {}".format(n, result.status))
