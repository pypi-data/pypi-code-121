from Cryptodome.PublicKey import RSA
from django.core.management.base import BaseCommand
from djangoldp_crypto.models import RSAKey


class Command(BaseCommand):
    help = 'Randomly generate a new RSA key for the DjangoLDP server'

    def handle(self, *args, **options):
        try:
            key = RSA.generate(2048)
            rsakey = RSAKey(priv_key=key.exportKey('PEM').decode('utf8'))
            rsakey.save()
            self.stdout.write('RSA key successfully created')
            self.stdout.write(u'Private key: \n{0}'.format(rsakey.priv_key))
            self.stdout.write(u'Public key: \n{0}'.format(rsakey.pub_key))
            self.stdout.write(u'Key ID: \n{0}'.format(rsakey.kid))
        except Exception as e:
            self.stdout.write('Something goes wrong: {0}'.format(e))
