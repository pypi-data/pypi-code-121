import time

from deque.deque_environment import AGENT_API_SERVICE_URL
from deque.redis_services import RedisServices
import pickle
from deque.rest_connect import RestConnect
class ParsingService:
    def __init__(self):
        self._redis = RedisServices.get_redis_connection()
        self._rest = RestConnect()
        self.tracking_endpoint = AGENT_API_SERVICE_URL+"/fex/python/track/"

    def receive(self):
        while True:
            submission_ids = self._redis.smembers("submission_ids:")
            #print(submission_ids)

            for s in submission_ids:
                steps = self._redis.smembers("submission_id:steps:"+s.decode("utf-8"))
                #print(steps)

                for step in steps:
                    key = "submission_id:step:data:"+str(s.decode("utf-8"))+str(step.decode("utf-8"))
                    pickled_data = self._redis.get(key)



                    if pickled_data is None:
                        continue

                    self._rest.post_binary(url=self.tracking_endpoint,data=pickled_data)
                    self._redis.delete(key)

                    #self._get_all_values(data)
            time.sleep(1)







    def _get_all_values(self, nested_dictionary):
        for key, value in nested_dictionary.items():
            if type(value) is dict:
                self._get_all_values(value)
            else:
                print(key, ":", value)

    def test(self):
        ex = {"k":"v"}
        pickled_object = pickle.dumps(ex)
        self._redis.set("test_key",pickled_object)
        data_p = self._redis.get("test_key")
        #self._redis.get("submission_id:step:data:test_submission30")
        print(pickle.loads(data_p))

if __name__ =="__main__":
    deque = ParsingService()
    deque.receive()









