from lpulive import User
import json
a = User(registration_no="11917210", password="Yeahhia#1236@")
# print(a.get_conversations())
print(a.send_message())
print("done")
# print(a.get_messages(1050467))
# with open("lpulive/test/data2.json","w") as f:
#     json.dump(a.get_messages(1050467),f,indent=4)
# print(a.get_chat_members(1992013))
# print(a.get_messages(chat_id=199201, msg_thread=False))
# print(a.get_message_threads(1991112, "36nje1uvhl.1ewef614sdfsdf925747748"))
