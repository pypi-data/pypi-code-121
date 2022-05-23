import os

AGENT_API_SERVICE_URL = 'https://apis-staging.deque.app'
api_environment = os.getenv("DEQUE_API_ENVIRONMENT")
REDIS_URL = "redis://localhost:6379"
if api_environment.lower() == "production":

    AGENT_API_SERVICE_URL = 'https://apis.deque.app'


else:

    AGENT_API_SERVICE_URL = 'https://apis-staging.deque.app'
    REDIS_URL = "redis://localhost:6379"
    #REDIS_URL = "redis://:czAr8PW5UuqvycZd0V9W0hPwum5m7yQV@redis-15261.c60.us-west-1-2.ec2.cloud.redislabs.com:15261/0"

