from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from djangoldp_account.models import LDPUser
import csv, unicodedata, re

class Command(BaseCommand):
    help = 'Import user list via CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

    def handle(self, *args, **options):
        nb = 0
        for row in csv.reader(open(options['csv_file'], 'rt')):
            # limit field size
            # strip to 30 letters because database field is limited to that size
            first_name = row[0][:min(len(row[0]), 30)]
            last_name = row[1][:min(len(row[1]), 30)]

            # check email correctness
            email = row[2]
            if not email:
                self.stdout.write(self.style.ERROR('user '+ first_name + ' ' + last_name + ' has no email'))
                continue
            if not re.match(r'[^\s]+@[^\s]+\.[^\s]+',email):
                self.stdout.write(self.style.ERROR('email address '+ email + ' has not been recognized as a valid one'))
                continue

            # compute username from first and last name (make sure there is no strange characters)
            username = unicodedata.normalize('NFD', first_name + last_name).encode('ascii', 'ignore').decode().lower().strip('.')
            username = re.sub(r'[\s\!#\$%&\'\*\^`\|~:\[\]\(\)\{\}=@\\/]+', r'-', username).strip('-')
            # strip to 50 letter because database field is limited to that size
            username = username[:min(len(username), 50)]

            # verify username and email uniqueness
            existing = LDPUser.objects.filter(email=email)
            if existing:
                self.stdout.write(self.style.ERROR(email + ' email address already taken by user ' + existing[0].username ))
                continue

            existing = LDPUser.objects.filter(username=username)
            if existing:
                done = False
                # try to add an integer at the end of the username
                for i in range(2,9):
                    second_try = username[:min(len(username), 49)] + str(i)
                    if not LDPUser.objects.filter(username=second_try):
                        username = second_try
                        break
                else:
                    self.stdout.write(self.style.ERROR(username + ' username is already taken by user ' + existing[0].first_name + ' ' + existing[0].last_name + ' (' + existing[0].email + ')' ))
                    continue

            # save the user
            self.stdout.write(first_name + ', ' + last_name + ', ' + username + ', ' + email)
            user = LDPUser(first_name=first_name, last_name=last_name, username=username, email=email)
            user.save()
            nb += 1

        self.stdout.write(self.style.SUCCESS(str(nb) + ' accounts imported successfully'))

