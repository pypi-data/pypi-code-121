import os
import cProfile
import time
from ..helpers import *
from ..mongo_engine import *
from datetime import datetime


def exponential_backoff(
        start_point=1, rate_gain=2, rate_type='exponential', max_time=100):
    '''
    for respecting other people's wishes

    the function that is passed in should raise an error (explicitly or implicitly) when output is not as desired
    for example if doing a url request and you get forbidden status (403), raise an error upon reception of that request code and
    this wrapper will handle exponentially backing off
    '''
    start_point = start_point
    rate_gain = rate_gain
    rate_type = rate_type
    max_time = max_time
    # logging.basicConfig(
    #     filename='/var/log/usr/exponential-backoffs.log', level=logging.INFO,
    #     format='%(asctime)s %(message)s')
    error = None

    def outer(func):

        def inner(*args, **kwargs):
            sleep = 0
            while True:
                try:
                    if sleep > max_time:
                        return "Failed to acquire"
                        # return logging.info(
                        #     f"Function {func.__name__} with args {args} and"
                        #     f" kwargs {kwargs} failed with error:\n       {error}"
                        # )
                    output = func(*args, **kwargs)
                    break
                except Exception as e:
                    if rate_type == 'exponential':
                        sleep = sleep * rate_gain or start_point
                    error = e
                    print(error)
                    print(
                        f"Exponentially backing off: waiting {sleep} seconds")
                    time.sleep(sleep)

            return output

        return inner
    return outer


# region *start* EXPONENTIAL BACKOFF PROOF/TESTING

# i = 0
# dict_ = {4: 'hey'}


# @exponential_backoff(rate_gain=4, max_time=4)
# def myfunc(a, b, c='this'):
#     global i, dict_
#     print(i)
#     i += 1
#     print(dict_[i])
#     return i

# endregion *end* EXPONENTIAL BACKOFF PROOF/TESTING


def update_db(interval=24):
    '''
    interval param indicates how long we wait (in hours) before grabbing value from the source
    '''

    interval = interval * 3600

    def outer(func):

        def inner(*args, **kwargs):

            # if datetime.datetime.now() - db_entry.last_updated

            return func(*args, **kwargs)

        return inner

    return outer


def memo(func):

    cache = {}

    def inner(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = func(*args)
            return result
        except TypeError:
            return func(*args)

    return inner


def db_lookup(db, coll, key, last_updated=24):
    '''
    This is essentially a memoize function for database lookups that sets the value if it doesn't \
      already exist or has surpassed the allotted last_updated time

    IMPORTANT: In order to use this decorator, one must specify a selection_filter kwarg \
      in the function that is wrapped by this decorator. The selection_filter value
      is a standard mongo filter selection object.
      This is necessary because there is no way to consistently pass dynamic values
      prior to the decorator being called

      So we find the document based on this and then update the desired <key> to the
      return value of our function

    EXAMPLE:

      @db_lookup('scraped_data', 'full_html', 'html')
      function get_html(self, selection_filter={'url': 'example_url'}):
        # return the html based on a get from <selection_filter[url]>

      That example function will first check the database for where url matches the example_url \
        and then if it doesnt exist or if its been greater than 24 hours since the field was last updated
        then it will return the html and db_lookup will automatically handle changing the last_updated field
        and the returned html to the html field

    IF THE VALUE DOES NOT EXIST IN THE DB THEN WE AUTOMATICALLY INSERT ONE; \
      ONLY THE VALUES PRESENT IN THE KEY AND THE SELECTION FILTER WILL
      BE DEFINED IN THE NEWLY CREATED DOCUMENT; OH AND last_updated will be included


    Parameters
    ----------

    db: str
      The MongoDB database you wish to connect to

    coll: str
      The MongoDB database collection you wish to check data from

    key: str
      The key value you wish to return

    last_updated: int or float
      How long (in hours) before a cached value is re-updated
    '''
    if last_updated:
        last_updated_seconds = last_updated * 3600
    db_ = MongoEngine(db=db, collection=coll)

    def outer(func):

        def inner(*args, **kwargs):
            document = db_.collection.find_one(kwargs['selection_filter'])
            if document:
                if last_updated_seconds:
                    now_ts = datetime.utcnow().timestamp()
                    document_ts = document['last_updated'].timestamp()
                    if now_ts - document_ts > last_updated_seconds:

                        value = func(*args, **kwargs)
                        db_.update_value(
                            kwargs['selection_filter'],
                            key, value, 'one')

                        return value

                print('Returning cached version')
                return document[key]

            else:
                value = func(*args, **kwargs)

                # instantiate new entry as the selection args
                new_entry = kwargs['selection_filter']

                # update that entry with our newly generated value and current time as last_updated
                new_entry.update({
                    'last_updated': datetime.utcnow(),
                    key: value
                })

                # add to the db
                db_.add_entry(new_entry)

                # return the value we initially were looking for
                return value

        return inner

    return outer
