# import asyncio

# from app.models import DeliveryZone
# from django.core.management.base import BaseCommand


# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         asyncio.run(self.async_handle(*args, **options))

#     async def async_handle(self, *args, **options):
#         await sio.emit("for admin", {}, to="users.admin")

#         from app.conf.server import sio
