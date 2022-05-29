"""Manager."""


import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Manager:
    """Mongo manager."""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    db_name: str = None

    async def connect(self, mongo_uri: str, db_name: str):
        """Open connection."""
        logging.debug('Connecting to MongoDB.')
        self.client = AsyncIOMotorClient(
            mongo_uri,
            maxPoolSize=10,
            minPoolSize=10)
        self.db_name = db_name
        self.db = self.client[self.db_name]
        logging.debug('Connected to MongoDB.')

    async def disconnect(self):
        """Close connection."""
        logging.debug('Closing connection with MongoDB.')
        self.client.close()
        logging.debug('Closed connection with MongoDB.')