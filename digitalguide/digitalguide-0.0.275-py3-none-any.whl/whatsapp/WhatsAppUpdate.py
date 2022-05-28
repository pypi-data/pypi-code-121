class WhatsAppUpdate:

    #CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('SmsMessageSid', 'SM1cea0a82154a503875f26e1898d972f2'), ('NumMedia', '0'), ('ProfileName', 'Sören'), ('SmsSid', 'SM1cea0a82154a503875f26e1898d972f2'), ('WaId', '4917652163847'), ('SmsStatus', 'received'), ('Body', 'Hi'), ('To', 'whatsapp:+14155238886'), ('NumSegments', '1'), ('MessageSid', 'SM1cea0a82154a503875f26e1898d972f2'), ('AccountSid', 'AC8f3944b5604c359ee4e1c882e64765e2'), ('From', 'whatsapp:+4917652163847'), ('ApiVersion', '2010-04-01')])])
    #CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('MediaContentType0', 'image/jpeg'), ('SmsMessageSid', 'MM94942a74f3cfc4fceed98eb6ec1ab15b'), ('NumMedia', '1'), ('ProfileName', 'Sören'), ('SmsSid', 'MM94942a74f3cfc4fceed98eb6ec1ab15b'), ('WaId', '4917652163847'), ('SmsStatus', 'received'), ('Body', ''), ('To', 'whatsapp:+14155238886'), ('NumSegments', '1'), ('MessageSid', 'MM94942a74f3cfc4fceed98eb6ec1ab15b'), ('AccountSid', 'AC8f3944b5604c359ee4e1c882e64765e2'), ('From', 'whatsapp:+4917652163847'), ('MediaUrl0', 'https://api.twilio.com/2010-04-01/Accounts/AC8f3944b5604c359ee4e1c882e64765e2/Messages/MM94942a74f3cfc4fceed98eb6ec1ab15b/Media/ME1eb56f5a20a667e7f4dc8428c04c1c36'), ('ApiVersion', '2010-04-01')])])
    # CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('Latitude', '52.406563'), ('Longitude', '12.969897'), ('SmsMessageSid', 'SM69ee3cde6532bdcedc2c44b83ee53f41'), ('NumMedia', '0'), ('ProfileName', 'Sören'), ('SmsSid', 'SM69ee3cde6532bdcedc2c44b83ee53f41'), ('WaId', '4917652163847'), ('SmsStatus', 'received'), ('Body', ''), ('To', 'whatsapp:+14155238886'), ('NumSegments', '1'), ('MessageSid', 'SM69ee3cde6532bdcedc2c44b83ee53f41'), ('AccountSid', 'AC8f3944b5604c359ee4e1c882e64765e2'), ('From', 'whatsapp:+4917652163847'), ('ApiVersio
    
    #CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('SmsMessageSid', 'SMfcee22301f5b6f136bb804f55e3b4c0a'), ('NumMedia', '0'), ('ProfileName', 'Sören'), ('SmsSid', 'SMfcee22301f5b6f136bb804f55e3b4c0a'), ('WaId', '4917652163847'), ('SmsStatus', 'received'), ('Body', 'start'), ('To', 'whatsapp:+18066055843'), ('MessagingServiceSid', 'MGd2b35b3b63c7c015da9063754f6087bf'), ('NumSegments', '1'), ('MessageSid', 'SMfcee22301f5b6f136bb804f55e3b4c0a'), ('AccountSid', 'AC8f3944b5604c359ee4e1c882e64765e2'), ('From', 'whatsapp:+4917652163847'), ('ApiVersion', '2010-04-01')])])
    def __init__(self, SmsMessageSid, NumMedia, ProfileName, SmsSid, WaId, SmsStatus, Body, To, NumSegments, MessageSid, AccountSid, From, ApiVersion, MessagingServiceSid=None, MediaContentType0=None, MediaUrl0=None, Latitude=None, Longitude=None, ReferralNumMedia=None) -> None:
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.SmsMessageSid = SmsMessageSid
        self.NumMedia = NumMedia
        self.ProfileName = ProfileName
        self.SmsSid = SmsSid
        self.WaId = WaId
        self.SmsStatus = SmsStatus
        self.Body = Body
        self.To = To
        self.NumSegments = NumSegments
        self.MessageSid = MessageSid
        self.AccountSid = AccountSid
        self.From = From
        self.ApiVersion = ApiVersion
        self.MediaContentType0 = MediaContentType0
        self.MediaUrl0 = MediaUrl0
        self.MessagingServiceSid = MessagingServiceSid
        self.ReferralNumMedia = ReferralNumMedia
